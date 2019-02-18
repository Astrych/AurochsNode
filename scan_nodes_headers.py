"""
Program checks hardcoded nodes headers data.
"""

from asyncio import get_event_loop, ensure_future, gather

from pinkcoin.node import Node
from pinkcoin.serializers import GetHeaders
from pinkcoin.params import HARDCODED_NODES


NODES = {}

class PinkcoinNode(Node):
    """
    Specific node implementation handling
    fetchng blockchain headers from nodes.
    """
    def __init__(self, ip, port):
        super().__init__(ip, port)
        self.send_per_peer = {}
        self.blocks_num_per_peer = {}

    async def handle_version(self, peer_name, message_header, message):
        print("-"*31)
        print(f"A version message from {peer_name} was received!")
        print("-"*31)
        print(message.user_agent)
        print(message.version)
        print(message.addr_recv)
        print(message.addr_from)
        print("-"*31)
        await super().handle_version(peer_name, message_header, message)

    async def handle_verack(self, peer_name, message_header, message):
        #pylint: disable=unused-argument
        """
        Handles Verack message.
        """
        print("="*31)
        print("A verack message was received!")
        print("="*31)
        send = self.send_per_peer.get(peer_name)
        if not send:
            genesis_block = 0x00000f79b700e6444665c4d090c9b8833664c4e2597c7087a6ba6391b956cc89
            print("Sending getheaders with genesis hash {}...".format(hex(genesis_block)))
            get_headers = GetHeaders([genesis_block])
            self.send_message(peer_name, get_headers)
            self.send_per_peer[peer_name] = True
        print("="*31)

    async def handle_inv(self, peer_name, message_header, message):
        #pylint: disable=unused-argument
        """
        Handles Inv message.
        """
        print("="*31)
        print("A inv message was received!")
        print("="*31)
        print(message.inventory)

    async def handle_headers(self, peer_name, message_header, message):
        #pylint: disable=unused-argument
        """
        Handles Headers message.
        """
        blocks_num = self.blocks_num_per_peer.get(peer_name, 0)
        if not blocks_num:
            self.blocks_num_per_peer[peer_name] = 0
        if blocks_num <= 765519:
            self.blocks_num_per_peer[peer_name] += len(message.headers)
            last_hash = message.headers[-1].calculate_hash()
            last_timestamp = message.headers[-1].timestamp
            if blocks_num > 765500:
                print("="*31)
                print("A headers message was received!")
                print("="*31)
                print("LEN:", len(message.headers))
                print("TOTAL:", blocks_num)
                print("="*31)
                # TODO: Save headers somewhere.
                print(f"Sending getheaders with hash {last_hash}")
                print(f"Sending getheaders with timstamp {last_timestamp}")
            get_headers = GetHeaders([int(last_hash, 16)])
            self.send_message(peer_name, get_headers)
        else:
            self.close_connection(peer_name)


if __name__ == "__main__":
    LOOP = get_event_loop()
    try:
        PINK_NODE = PinkcoinNode("0.0.0.0", "9134")
        WORK_TO_DO = [
            ensure_future(PINK_NODE.connect(v["ip"], v["port"])) for v in HARDCODED_NODES.values()
        ]
        LOOP.run_until_complete(gather(*WORK_TO_DO))
    except KeyboardInterrupt:
        pass
    finally:
        pass
