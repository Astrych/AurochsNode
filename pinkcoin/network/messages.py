"""
List of all network messages.
"""

from .core import serializers as core
from .secure_messages import serializers as smsg


MESSAGE_MAPPING = {
    "version": core.VersionSerializer,
    "verack": core.VerAckSerializer,
    "ping": core.PingSerializer,
    "pong": core.PongSerializer,
    "inv": core.InventoryVectorSerializer,
    "addr": core.AddressVectorSerializer,
    "getdata": core.GetDataSerializer,
    "notfound": core.NotFoundSerializer,
    "tx": core.TxSerializer,
    "block": core.BlockSerializer,
    "headers": core.HeaderVectorSerializer,
    "mempool": core.MemPoolSerializer,
    "getaddr": core.GetAddrSerializer,
    "getblocks": core.GetBlocksSerializer,
    "getheaders": core.GetHeadersSerializer,
    "alert": core.AlertSerializer,

    # Network messages of secure messages protocol.
    # "smsgInv":,
    # "smsgShow":,
    # "smsgHave":,
    # "smsgWant":,
    # "smsgMsg":,
    # "smsgMatch":,
    "smsgPing": smsg.SecureMessagesPingSerializer,
    "smsgPong": smsg.SecureMessagePongSerializer,
    # "smsgDisabled":,
    # "smsgIgnore":,
}
