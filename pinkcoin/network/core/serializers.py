"""
Serializers for core (protocol consensus) messages.
"""

import time
import random
import hashlib

from ..base_serializer import Serializer, SerializableMessage
from .. import data_fields
from .. import params
from .. import utils


class IPv4Address:
    """
    The IPv4 Address (without timestamp).
    """
    def __init__(self):
        self.services = params.SERVICES["NODE_NETWORK"]
        self.ip_address = "0.0.0.0"
        self.port = 9134

    def __repr__(self):
        services = utils.services_to_text(self.services)
        if not services:
            services = "No Services"
        return "<{} IP=[{}:{}] Services={}>".format(
            self.__class__.__name__, self.ip_address, self.port, services
        )

class IPv4AddressSerializer(Serializer):
    """
    Serializer for the IPv4Address.
    """
    model_class = IPv4Address

    services = data_fields.UInt64LEField()
    ip_address = data_fields.IPv4AddressField()
    port = data_fields.UInt16BEField()

class IPv4AddressTimestamp(IPv4Address):
    """
    The IPv4 Address with timestamp.
    """
    def __init__(self):
        super().__init__()
        self.timestamp = int(time.time())

    def __repr__(self):
        services = utils.services_to_text(self.services)
        if not services:
            services = "No Services"
        return "<{} Timestamp=[{}] IP=[{}:{}] Services={}>".format(
            self.__class__.__name__, time.ctime(self.timestamp),
            self.ip_address, self.port, services
        )

class IPv4AddressTimestampSerializer(Serializer):
    """
    Serializer for the IPv4AddressTimestamp.
    """
    model_class = IPv4AddressTimestamp

    timestamp = data_fields.UInt32LEField()
    services = data_fields.UInt64LEField()
    ip_address = data_fields.IPv4AddressField()
    port = data_fields.UInt16BEField()

class Version(SerializableMessage):
    """
    The version command.
    """
    command = "version"

    def __init__(self):
        self.version = params.PROTOCOL_VERSION
        self.services = params.SERVICES["NODE_NETWORK"]
        self.timestamp = int(time.time())
        self.addr_recv = IPv4Address()
        self.addr_from = IPv4Address()
        self.nonce = random.randint(0, 2**32-1)
        self.user_agent = "/pink-scanner:0.0.1/"
        self.start_height = 0

class VersionSerializer(Serializer):
    """
    The version command serializer.
    """
    model_class = Version

    version = data_fields.Int32LEField()
    services = data_fields.UInt64LEField()
    timestamp = data_fields.Int64LEField()
    addr_recv = data_fields.NestedField(IPv4AddressSerializer)
    addr_from = data_fields.NestedField(IPv4AddressSerializer)
    nonce = data_fields.UInt64LEField()
    user_agent = data_fields.VariableStringField()
    start_height = data_fields.Int32LEField()

class VerAck(SerializableMessage):
    """
    The version acknowledge (verack) command.
    """
    command = "verack"

class VerAckSerializer(Serializer):
    """
    The serializer for the verack command.
    """
    model_class = VerAck

class Ping(SerializableMessage):
    """
    The ping command, which should always be
    answered with a Pong.
    """
    command = "ping"

    def __init__(self):
        self.nonce = random.randint(0, 2**32-1)

    def __repr__(self):
        return f"<{self.__class__.__name__} Nonce=[{self.nonce}]>"

class PingSerializer(Serializer):
    """
    The ping command serializer.
    """
    model_class = Ping

    nonce = data_fields.UInt64LEField()

class Pong(SerializableMessage):
    """
    The pong command, usually returned when
    a ping command arrives.
    """
    command = "pong"

    def __init__(self):
        self.nonce = random.randint(0, 2**32-1)

    def __repr__(self):
        return f"<{self.__class__.__name__} Nonce=[{self.nonce}]>"

class PongSerializer(Serializer):
    """
    The pong command serializer.
    """
    model_class = Pong

    nonce = data_fields.UInt64LEField()

# TODO: Check if that inheritance is necessary (SerializableMessage).
# There is no command set here and is not a protocol message.
class Inventory(SerializableMessage):
    """
    The Inventory representation.
    """
    def __init__(self):
        self.inv_type = params.INVENTORY_TYPE["MSG_TX"]
        self.inv_hash = 0

    def type_to_text(self):
        """
        Converts the inventory type to text representation.
        """
        for key, value in params.INVENTORY_TYPE.items():
            if value == self.inv_type:
                return key
        return "Unknown Type"

    def __repr__(self):
        return "<{} Type=[{}] Hash=[{:x}]>".format(
            self.__class__.__name__, self.type_to_text(), self.inv_hash
        )

class InventorySerializer(Serializer):
    """
    The serializer for the Inventory.
    """
    model_class = Inventory

    inv_type = data_fields.UInt32LEField()
    inv_hash = data_fields.Hash()

class InventoryVector(SerializableMessage):
    """
    A vector of inventories.
    """
    command = "inv"

    def __init__(self):
        self.inventory = []

    def __repr__(self):
        return f"<{self.__class__.__name__} Count=[{len(self)}]>"

    def __len__(self):
        return len(self.inventory)

    def __iter__(self):
        return iter(self.inventory)

class InventoryVectorSerializer(Serializer):
    """
    The serializer for the vector of inventories.
    """
    model_class = InventoryVector

    inventory = data_fields.ListField(InventorySerializer)

class AddressVector(SerializableMessage):
    """
    A vector of addresses.
    """
    command = "addr"

    def __init__(self):
        self.addresses = []

    def __repr__(self):
        return f"<{self.__class__.__name__} Count=[{len(self)}]>"

    def __len__(self):
        return len(self.addresses)

    def __iter__(self):
        return iter(self.addresses)

class AddressVectorSerializer(Serializer):
    """
    Serializer for the addresses vector.
    """
    model_class = AddressVector

    addresses = data_fields.ListField(IPv4AddressTimestampSerializer)

class GetData(InventoryVector):
    """
    GetData message command.
    """
    command = "getdata"

class GetDataSerializer(Serializer):
    """
    Serializer for the GetData command.
    """
    model_class = GetData

    inventory = data_fields.ListField(InventorySerializer)

class NotFound(GetData):
    """
    NotFound command message.
    """
    command = "notfound"

class NotFoundSerializer(Serializer):
    """
    Serializer for the NotFound message.
    """
    model_class = NotFound

    inventory = data_fields.ListField(InventorySerializer)

class OutPoint:
    """
    The OutPoint representation.
    """
    def __init__(self):
        self.out_hash = 0
        self.index = 0

    def __repr__(self):
        return "<{} Index=[{}] Hash=[{:x}]>".format(
            self.__class__.__name__, self.index, self.out_hash
        )

class OutPointSerializer(Serializer):
    """
    The OutPoint representation serializer.
    """
    model_class = OutPoint

    out_hash = data_fields.Hash()
    index = data_fields.UInt32LEField()

class TxIn:
    """
    The transaction input representation.
    """
    def __init__(self):
        self.previous_output = None
        self.signature_script = "Empty"
        # See https://en.bitcoin.it/wiki/Protocol_specification#tx for definition.
        # Basically, this field should always be UINT_MAX, i.e. int("ffffffff", 16)
        self.sequence = 4294967295

    def __repr__(self):
        return f"<{self.__class__.__name__} Sequence=[{self.sequence}]>"

class TxInSerializer(Serializer):
    """
    The transaction input serializer.
    """
    model_class = TxIn

    previous_output = data_fields.NestedField(OutPointSerializer)
    signature_script = data_fields.VariableStringField()
    sequence = data_fields.UInt32LEField()

class TxOut:
    """
    The transaction output.
    """
    def __init__(self):
        self.value = 0
        self.pk_script = "Empty"

    def get_pink_value(self):
        """
        Returns coins value in PINK.
        """
        return self.value//100000000 + self.value%100000000/100000000.0

    def __repr__(self):
        return "<{} Value=[{:.8f}]>".format(self.__class__.__name__, self.get_pink_value())

class TxOutSerializer(Serializer):
    """
    The transaction output serializer.
    """
    model_class = TxOut

    value = data_fields.Int64LEField()
    pk_script = data_fields.VariableStringField()

class Tx(SerializableMessage):
    """
    The main transaction representation, this object will
    contain all the inputs and outputs of the transaction.
    """
    command = "tx"

    def __init__(self):
        self.version = 1
        self.tx_in = []
        self.tx_out = []
        self.lock_time = 0

    def _locktime_to_text(self):
        """
        Converts the lock-time to textual representation.
        """
        text = "Unknown"
        if self.lock_time == 0:
            text = "Always Locked"
        elif self.lock_time < 500000000:
            text = f"Block {self.lock_time}"
        elif self.lock_time >= 500000000:
            text = time.ctime(self.lock_time)
        return text

    def calculate_hash(self):
        """
        This method will calculate the hash of the transaction.
        """
        hash_fields = ["version", "tx_in", "tx_out", "lock_time"]
        serializer = TxSerializer()
        bin_data = serializer.serialize(self, hash_fields)
        tx_hash = hashlib.sha256(bin_data).digest()
        tx_hash = hashlib.sha256(tx_hash).digest()
        return tx_hash[::-1].encode("hex_codec")

    def __repr__(self):
        return "<{} Version=[{}] Lock Time=[{}] TxIn Count=[{}] Hash=[{}] TxOut Count=[{}]>".format(
            self.__class__.__name__, self.version, self._locktime_to_text(),
            len(self.tx_in), self.calculate_hash(), len(self.tx_out)
        )

class TxSerializer(Serializer):
    """
    The transaction serializer.
    """
    model_class = Tx

    version = data_fields.UInt32LEField()
    tx_in = data_fields.ListField(TxInSerializer)
    tx_out = data_fields.ListField(TxOutSerializer)
    lock_time = data_fields.UInt32LEField()

# TODO: Check if that inheritance is necessary (SerializableMessage).
# There is no command set here and is not a protocol message.
class BlockHeader(SerializableMessage):
    """
    The header of the block.
    """
    def __init__(self):
        self.version = 0
        self.prev_block = 0
        self.merkle_root = 0
        self.timestamp = 0
        self.bits = 0
        self.nonce = 0
        # Dummy fields to make parsing BlockHeader
        # compatible with Block parsing.
        self.txns_count = 0
        self.sig = 0

    def calculate_hash(self):
        """
        This method will calculate the hash of the block.
        """
        hash_fields = [
            "version", "prev_block", "merkle_root",
            "timestamp", "bits", "nonce"
        ]
        serializer = BlockSerializer()
        bin_data = serializer.serialize(self, hash_fields)
        header_hash = hashlib.scrypt(
            password=bin_data, salt=bin_data, n=1024, r=1, p=1, maxmem=0, dklen=32
        )
        header_hash = int.from_bytes(header_hash, byteorder="little")
        return "{0:#0{1}x}".format(header_hash, 66)

    def __repr__(self):
        return "<{} Version=[{}] Timestamp=[{}] Nonce=[{}] Hash=[{}] Tx Count=[{}]>".format(
            self.__class__.__name__, self.version, time.ctime(self.timestamp),
            self.nonce, self.calculate_hash(), self.txns_count
        )

class BlockHeaderSerializer(Serializer):
    """
    The serializer for the block header.
    """
    model_class = BlockHeader

    version = data_fields.UInt32LEField()
    prev_block = data_fields.Hash()
    merkle_root = data_fields.Hash()
    timestamp = data_fields.UInt32LEField()
    bits = data_fields.UInt32LEField()
    nonce = data_fields.UInt32LEField()
    txns_count = data_fields.VariableIntegerField()
    sig = data_fields.VariableIntegerField()

class Block(BlockHeader):
    """
    The block message. This message contains all the transactions
    present in the block.
    """
    command = "block"

    def __init__(self):
        # super().__init__()
        self.version = 0
        self.prev_block = 0
        self.merkle_root = 0
        self.timestamp = 0
        self.bits = 0
        self.nonce = 0
        self.txns = []
        self.block_sig = 0

    def __len__(self):
        return len(self.txns)

    def __iter__(self):
        return iter(self.txns)

    def __repr__(self):
        return "<{} Version=[{}] Timestamp=[{}] Nonce=[{}] Hash=[{}] Tx Count=[{}]>".format(
            self.__class__.__name__, self.version, time.ctime(self.timestamp),
            self.nonce, self.calculate_hash(), len(self)
        )

class BlockSerializer(Serializer):
    """
    The deserializer for the blocks.
    """
    model_class = Block

    version = data_fields.UInt32LEField()
    prev_block = data_fields.Hash()
    merkle_root = data_fields.Hash()
    timestamp = data_fields.UInt32LEField()
    bits = data_fields.UInt32LEField()
    nonce = data_fields.UInt32LEField()
    txns = data_fields.ListField(TxSerializer)
    block_sig = data_fields.VariableStringField()

class HeaderVector(SerializableMessage):
    """
    The header only vector.
    """
    command = "headers"

    def __init__(self):
        self.headers = []

    def __repr__(self):
        return f"<{self.__class__.__name__} Count=[{len(self)}]>"

    def __len__(self):
        return len(self.headers)

    def __iter__(self):
        return iter(self.headers)

class HeaderVectorSerializer(Serializer):
    """
    Serializer for the block header vector.
    """
    model_class = HeaderVector

    headers = data_fields.ListField(BlockHeaderSerializer)

class MemPool(SerializableMessage):
    """
    The mempool command.
    """
    command = "mempool"

class MemPoolSerializer(Serializer):
    """
    The serializer for the mempool command.
    """
    model_class = MemPool

class GetAddr(SerializableMessage):
    """
    The getaddr command.
    """
    command = "getaddr"

class GetAddrSerializer(Serializer):
    """
    The serializer for the getaddr command.
    """
    model_class = GetAddr

class GetBlocks(SerializableMessage):
    """
    The getblocks command.
    """
    command = "getblocks"

    def __init__(self, hashes):
        self.version = params.PROTOCOL_VERSION
        self.hash_count = len(hashes)
        self.hash_stop = 0
        self.block_hashes = hashes

class GetBlocksSerializer(Serializer):
    """
    Serializer for getblocks message.
    """
    model_class = GetBlocks

    version = data_fields.UInt32LEField()
    hash_count = data_fields.VariableIntegerField()
    block_hashes = data_fields.BlockLocator()
    hash_stop = data_fields.Hash()

class GetHeaders(SerializableMessage):
    """
    The getheaders command.
    """
    command = "getheaders"

    def __init__(self, hashes):
        self.version = params.PROTOCOL_VERSION
        self.hash_count = len(hashes)
        self.hash_stop = 0
        self.block_hashes = hashes

class GetHeadersSerializer(Serializer):
    """
    Serializer for getheaders message.
    """
    model_class = GetHeaders

    version = data_fields.UInt32LEField()
    hash_count = data_fields.VariableIntegerField()
    block_hashes = data_fields.BlockLocator()
    hash_stop = data_fields.Hash()

class Alert(SerializableMessage):
    """
    The alert command.
    """
    command = "alert"

    def __init__(self):
        self.payload = ""
        self.signature = ""

    def __repr__(self):
        return "<{} Payload=[{}], Signature=[{}]>".format(
            self.__class__.__name__, self.payload, self.signature,
        )

class AlertSerializer(Serializer):
    """
    The alert command serializer.
    """
    model_class = Alert

    payload = data_fields.VariableStringField()
    signature = data_fields.VariableStringField()

class CancelAlert:
    """
    The cancel alert field representation.
    """
    def __init__(self):
        self.cancel = 0

class CancelAlertSerializer(Serializer):
    """
    The cancel alert serializer.
    """
    model_class = CancelAlert

    cancel = data_fields.Int32LEField()

class SubVerAlert:
    """
    The SubVer alert field representation.
    """
    def __init__(self):
        self.sub_ver = 0

class SubVerAlertSerializer(Serializer):
    """
    The SubVer alert serializer.
    """
    model_class = SubVerAlert

    sub_ver = data_fields.VariableStringField()

class AlertPayload:
    """
    The alert message payload representation.
    """
    def __init__(self):
        self.version = 0
        self.relay_until = 0
        self.expiration = 0
        self.alert_id = 0
        self.cancel = 0
        self.set_cancel = []
        self.min_ver = 0
        self.max_ver = 0
        self.set_sub_ver = []
        self.priority = 0
        self.comment = ""
        self.status_bar = ""
        self.reserved = ""

    def __repr__(self):
        return f"<{self.__class__.__name__} Message=[{self.status_bar}]>"

class AlertPayloadSerializer(Serializer):
    """
    The alert payload serializer.
    """
    model_class = AlertPayload

    version = data_fields.Int32LEField()
    relay_until = data_fields.Int64LEField()
    expiration = data_fields.Int64LEField()
    alert_id = data_fields.Int32LEField()
    cancel = data_fields.Int32LEField()
    set_cancel = data_fields.ListField(CancelAlertSerializer)
    min_ver = data_fields.Int32LEField()
    max_ver = data_fields.Int32LEField()
    set_sub_ver = data_fields.ListField(SubVerAlertSerializer)
    priority = data_fields.Int32LEField()
    comment = data_fields.VariableStringField()
    status_bar = data_fields.VariableStringField()
    reserved = data_fields.VariableStringField()
