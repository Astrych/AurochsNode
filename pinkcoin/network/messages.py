"""
List of all network messages.
"""

from .core import serializers as core
from .secure_messages import serializers as smsg


MESSAGE_MAPPING = {
    # Network commands for main (core) consensus protocol.
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

    # Network commands for secure messages protocol.
    "smsgInv": smsg.SecureMessagesInventorySerializer,
    # "smsgShow":,
    # "smsgHave":,
    # "smsgWant":,
    # "smsgMsg":,
    # "smsgMatch":,
    "smsgPing": smsg.SecureMessagesPingSerializer,
    "smsgPong": smsg.SecureMessagePongSerializer,
    "smsgDisabled": smsg.SecureMessageDisabledSerializer,
    "smsgIgnore": smsg.SecureMessageIgnoreSerializer,
}
