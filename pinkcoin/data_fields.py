"""Module with serializable fields
used by serializators/deserializators
"""

from io import BytesIO
import struct
import socket


# pylint: disable=E1101
class Field:
    """Base class for the Fields. This class only implements
    the counter to keep the order of the fields on the
    serializer classes.
    """
    counter = 0

    def __init__(self):
        self.count = Field.counter
        Field.counter += 1

    def parse(self, value):
        """This method should be implemented to parse the value
        parameter into the field internal representation.

        :param value: value to be parsed
        """
        raise NotImplementedError

    def deserialize(self, stream):
        """This method must read the stream data and then
        deserialize and return the deserialized content.

        :returns: the deserialized content
        :param stream: stream of data to read
        """
        raise NotImplementedError

    def serialize(self):
        """Serialize the internal representation and return
        the serialized data.

        :returns: the serialized data
        """
        raise NotImplementedError

    def __repr__(self):
        return "<%s [%r]>" % (
            self.__class__.__name__,
            repr(self.value)
        )

    def __str__(self):
        return str(self.value)

class PrimaryField(Field):
    """This is a base class for all fields that has only
    one value and their value can be represented by
    a Python struct datatype.

    Example of use::

        class UInt32LEField(PrimaryField):
            datatype = "<I"
    """

    def parse(self, value):
        """This method will set the internal value to the
        specified value.

        :param value: the value to be set
        """
        self.value = value

    def deserialize(self, stream):
        """Deserialize the stream using the struct data type
        specified.

        :param stream: the data stream
        """
        data_size = struct.calcsize(self.datatype)
        data = stream.read(data_size)
        return struct.unpack(self.datatype, data)[0]

    def serialize(self):
        """Serialize the internal data and then return the
        serialized data."""
        data = struct.pack(self.datatype, self.value)
        return data

class Int32LEField(PrimaryField):
    """32-bit little-endian integer field.
    """
    datatype = "<i"

class UInt32LEField(PrimaryField):
    """32-bit little-endian unsigned integer field.
    """
    datatype = "<I"

class Int64LEField(PrimaryField):
    """64-bit little-endian integer field.
    """
    datatype = "<q"

class UInt64LEField(PrimaryField):
    """64-bit little-endian unsigned integer field.
    """
    datatype = "<Q"

class Int16LEField(PrimaryField):
    """16-bit little-endian integer field.
    """
    datatype = "<h"

class UInt16LEField(PrimaryField):
    """16-bit little-endian unsigned integer field.
    """
    datatype = "<H"

class UInt16BEField(PrimaryField):
    """16-bit big-endian unsigned integer field.
    """
    datatype = ">H"

class FixedStringField(Field):
    """A fixed length string field.

    Example of use::

        class MessageHeaderSerializer(Serializer):
            model_class = MessageHeader
            magic = fields.UInt32LEField()
            command = fields.FixedStringField(12)
            length = fields.UInt32LEField()
            checksum = fields.UInt32LEField()
    """
    def __init__(self, length):
        super().__init__()
        self.length = length

    def parse(self, value):
        self.value = value[:self.length]

    def deserialize(self, stream):
        data = stream.read(self.length)
        return data[:(data+b'\x00').index(b'\x00')].decode("utf-8")

    def serialize(self):
        bin_data = BytesIO()
        bin_data.write(struct.pack("12s", self.value.encode("utf-8")))
        return bin_data.getvalue()

class NestedField(Field):
    """A field used to nest another serializer.

    Example of use::

        class TxInSerializer(Serializer):
            model_class = TxIn
            previous_output = fields.NestedField(OutPointSerializer)
            signature_script = fields.VariableStringField()
            sequence = fields.UInt32LEField()
    """
    def __init__(self, serializer_class):
        super().__init__()
        self.serializer_class = serializer_class
        self.serializer = self.serializer_class()

    def parse(self, value):
        self.value = value

    def deserialize(self, stream):
        return self.serializer.deserialize(stream)

    def serialize(self):
        return self.serializer.serialize(self.value)

class ListField(Field):
    """A field used to serialize/deserialize a list of serializers.

    Example of use::

        class TxSerializer(Serializer):
            model_class = Tx
            version = fields.UInt32LEField()
            tx_in = fields.ListField(TxInSerializer)
            tx_out = fields.ListField(TxOutSerializer)
            lock_time = fields.UInt32LEField()
    """
    def __init__(self, serializer_class):
        super().__init__()
        self.serializer_class = serializer_class
        self.var_int = VariableIntegerField()

    def parse(self, value):
        self.value = value

    def serialize(self):
        bin_data = BytesIO()
        self.var_int.parse(len(self))
        bin_data.write(self.var_int.serialize())
        serializer = self.serializer_class()
        for item in self:
            bin_data.write(serializer.serialize(item))
        return bin_data.getvalue()

    def deserialize(self, stream):
        count = self.var_int.deserialize(stream)
        items = []
        serializer = self.serializer_class()
        for _ in range(count):
            data = serializer.deserialize(stream)
            items.append(data)
        return items

    def __iter__(self):
        return iter(self.value)

    def __len__(self):
        return len(self.value)

class IPv4AddressField(Field):
    """An IPv4 address field without timestamp and reserved IPv6 space.
    """
    reserved = b"\x00"*10 + b"\xff"*2

    def parse(self, value):
        self.value = value

    def deserialize(self, stream):
        unused_reserved = stream.read(12)
        addr = stream.read(4)
        return socket.inet_ntoa(addr)

    def serialize(self):
        bin_data = BytesIO()
        bin_data.write(self.reserved)
        bin_data.write(socket.inet_aton(self.value))
        return bin_data.getvalue()

class VariableIntegerField(Field):
    """A variable size integer field.
    """
    def parse(self, value):
        self.value = int(value)

    def deserialize(self, stream):
        int_id_raw = stream.read(struct.calcsize("<B"))
        int_id = struct.unpack("<B", int_id_raw)[0]
        if int_id == 0xFD:
            data = stream.read(2)
            int_id = struct.unpack("<H", data)[0]
        elif int_id == 0xFE:
            data = stream.read(4)
            int_id = struct.unpack("<I", data)[0]
        elif int_id == 0xFF:
            data = stream.read(8)
            int_id = struct.unpack("<Q", data)[0]
        return int_id

    def serialize(self):
        if self.value < 0xFD:
            return struct.pack("B", self.value)
        if self.value <= 0xFFFF:
            return b'\xFD' + struct.pack("<H", self.value)
        if self.value <= 0xFFFFFFFF:
            return b'\xFE' + struct.pack("<I", self.value)
        return b'\xFF' + struct.pack("<Q", self.value)

class VariableStringField(Field):
    """A variable length string field.
    """
    def __init__(self):
        super().__init__()
        self.var_int = VariableIntegerField()

    def parse(self, value):
        self.value = str(value)

    def deserialize(self, stream):
        string_length = self.var_int.deserialize(stream)
        string_data = stream.read(string_length)
        return string_data

    def serialize(self):
        self.var_int.parse(len(self))
        bin_data = BytesIO()
        bin_data.write(self.var_int.serialize())
        bin_data.write(bytes(self.value, "utf-8"))
        return bin_data.getvalue()

    def __len__(self):
        return len(self.value)

class Hash(Field):
    """A hash type field.
    """
    datatype = "<I"

    def parse(self, value):
        self.value = value

    def deserialize(self, stream):
        data_size = struct.calcsize(self.datatype)
        intvalue = 0
        for i in range(8):
            data = stream.read(data_size)
            val = struct.unpack(self.datatype, data)[0]
            intvalue += val << (i * 32)
        return intvalue

    def serialize(self):
        hash_ = self.value
        bin_data = BytesIO()
        for _ in range(8):
            pack_data = struct.pack(self.datatype, hash_ & 0xFFFFFFFF)
            bin_data.write(pack_data)
            hash_ >>= 32
        return bin_data.getvalue()

class BlockLocator(Field):
    # pylint: disable=abstract-method
    """A block locator type used for getblocks and getheaders.
    """
    datatype = "<I"

    def parse(self, value):
        self.values = value

    def serialize(self):
        bin_data = BytesIO()
        for hash_ in self.values:
            for _ in range(8):
                pack_data = struct.pack(self.datatype, hash_ & 0xFFFFFFFF)
                bin_data.write(pack_data)
                hash_ >>= 32
        return bin_data.getvalue()
