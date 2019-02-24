"""
Base serializer module handling protocol messages
serialization and deserialization.
"""

import struct
import hashlib
from io import BytesIO
from collections import OrderedDict

from . import data_fields
from . import params


# pylint: disable=E1101
class SerializerMeta(type):
    """
    The serializer meta class. This class will create an attribute
    called '_fields' in each serializer with the ordered dict of
    fields present on the subclasses.
    """
    def __new__(cls, name, bases, attrs):
        attrs["_fields"] = cls.get_fields(bases, attrs, data_fields.Field)
        return super().__new__(cls, name, bases, attrs)

    @classmethod
    def get_fields(cls, bases, attrs, field_class):
        """
        This method will construct an ordered dict with all
        the fields present on the serializer classes.
        """
        fields = [
            (field_name, attrs.pop(field_name))
            for field_name, field_value in list(attrs.items())
            if isinstance(field_value, field_class)
        ]

        for base_cls in bases[::-1]:
            if hasattr(base_cls, "_fields"):
                fields = list(base_cls._fields.items()) + fields

        fields.sort(key=lambda it: it[1].count)
        return OrderedDict(fields)

class SerializerABC(metaclass=SerializerMeta):
    """
    The serializer abstract base class.
    """

class Serializer(SerializerABC):
    """
    The main serializer class, inherit from this class to
    create custom serializers.

    Example of use::

        class VerAckSerializer(Serializer):
            model_class = VerAck
    """
    def serialize(self, obj, fields=None):
        """
        This method will receive an object and then will serialize
        it according to the fields declared on the serializer.

        :param obj: The object to serializer.
        """
        bin_data = BytesIO()
        for field_name, field_obj in self._fields.items():
            if fields:
                if field_name not in fields:
                    continue
            attr = getattr(obj, field_name, None)
            field_obj.parse(attr)
            bin_data.write(field_obj.serialize())

        return bin_data.getvalue()

    def deserialize(self, stream):
        """
        This method will read the stream and then will deserialize the
        binary data information present on it.

        :param stream: A file-like object (BytesIO, file, socket, etc.)
        """
        model = self.model_class()
        for field_name, field_obj in self._fields.items():
            value = field_obj.deserialize(stream)
            setattr(model, field_name, value)
        return model

class SerializableMessage:
    """
    Represents message serialized to object.
    """
    def get_message(self, network_type="main"):
        """Get the binary version of this message, complete with header."""
        from . import messages

        message_header = MessageHeader(network_type)
        message_header_serial = MessageHeaderSerializer()

        serializer = messages.MESSAGE_MAPPING[self.command]()
        bin_message = serializer.serialize(self)
        payload_checksum = MessageHeaderSerializer.calc_checksum(bin_message)
        message_header.checksum = payload_checksum
        message_header.length = len(bin_message)
        message_header.command = self.command

        bin_header = message_header_serial.serialize(message_header)
        return bin_header + bin_message

class MessageHeader:
    """
    The header of all network messages.
    """
    def __init__(self, network_type="main"):
        self.magic = params.MAGIC_VALUES[network_type]
        self.command = "None"
        self.length = 0
        self.checksum = 0

    def _magic_to_text(self):
        """
        Converts the magic value to a textual representation.
        """
        for key, value in params.MAGIC_VALUES.items():
            if value == self.magic:
                return key
        return "Unknown Magic"

    def __repr__(self):
        return "<{} Magic=[{}] Length=[{}] Checksum=[{}]>".format(
            self.__class__.__name__, self._magic_to_text(),
            self.length, self.checksum
        )

class MessageHeaderSerializer(Serializer):
    """
    Serializer for the MessageHeader.
    """
    model_class = MessageHeader

    magic = data_fields.UInt32LEField()
    command = data_fields.FixedStringField(12)
    length = data_fields.UInt32LEField()
    checksum = data_fields.UInt32LEField()

    @staticmethod
    def calcsize():
        """
        Calculates header size.
        """
        return struct.calcsize("i12sii")

    @staticmethod
    def calc_checksum(payload):
        """
        Calculate the checksum of the specified payload.

        :param payload: The binary data payload.
        """
        sha256hash = hashlib.sha256(payload)
        sha256hash = hashlib.sha256(sha256hash.digest())
        checksum = sha256hash.digest()[:4]
        return struct.unpack("<I", checksum)[0]
