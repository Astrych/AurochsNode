"""Module with various network parameters.
"""


# The protocol version.
PROTOCOL_VERSION = 60016

# The network magic values.
MAGIC_VALUES = {
    "main": 0xFBF9F4F2,
    "test": 0x0D050402,
}

# The available services.
SERVICES = {
    "NODE_NONE": 0,
    # A services flag that denotes whether the peer has a copy of the block chain or not.
    "NODE_NETWORK": (1 << 0),
    # A flag that denotes whether the peer supports the getutxos message or not.
    # Command is used to request unspent transaction information based on the given
    # outpoints, while the utxos command is the response.
    "NODE_GETUTX0": (1 << 1),
    "NODE_BLOOM": (1 << 2),
    "NODE_WITNESS": (1 << 3),
    "NODE_XTHIN": (1 << 4),
    "NODE_NETWORK_LIMITED": (1 << 10),
}

# The type of the inventories.
INVENTORY_TYPE = {
    "ERROR": 0,
    "MSG_TX": 1,
    "MSG_BLOCK": 2,
}

HARDCODED_NODES = {
    "my_node_on_aws": {"ip": "18.224.37.139", "port": 9134},
    "tokyo.pinkarmy.ml": {"ip": "45.32.49.237", "port": 9134},
    "sydney.pinkarmy.ml": {"ip": "45.76.125.31", "port": 9134},
    "singapore.pinkarmy.ml": {"ip": "45.77.36.238", "port": 9134},
    "paris.pinkarmy.ml": {"ip": "217.69.6.86", "port": 9134},
    "frankfurt.pinkarmy.ml": {"ip": "95.179.165.154", "port": 9134},
    "primary": {"ip": "159.203.20.96", "port": 9134},
}
