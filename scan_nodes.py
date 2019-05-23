"""
Program connects to list of hardcoded nodes and asks them for
their peers. After that it uses these peers to repeat the process.
That way it builds list of all recently seen peers in the network.
"""

import json
from datetime import datetime
from time import time
from asyncio import get_event_loop, ensure_future, gather
from typing import Dict

from pinkcoin.network.node import Node
from pinkcoin.network.core.serializers import GetHeaders
from pinkcoin.network.params import HARDCODED_NODES


NODES: Dict = {}

class TestAddrNode(Node):
    """
    """
    def __init__(self, ip, port):
        super().__init__(ip, port)
        self.send_per_peer = {}
        self.blocks_num_per_peer = {}

    async def handle_version(self, peer_name, message_header, message):
        my_time = time()
        print("-"*31)
        print(f"A version message from {peer_name} was received!")
        print("-"*31)
        print(message.user_agent)
        print(message.version)
        print(message.addr_recv)
        print(message.addr_from)
        print(message.timestamp)
        print(datetime.utcfromtimestamp(message.timestamp).strftime("%Y-%m-%d %H:%M:%S"))
        print("TIME DIFF: ", message.timestamp - my_time)
        print("-"*31)

        if peer_name not in NODES:
            NODES[peer_name] = {
                "version": message.version,
                "agent": message.user_agent.decode("utf-8"),
                "offset": message.timestamp - my_time,
                "last_header": None,
                "performance_time": None,
            }

        await super().handle_version(peer_name, message_header, message)

    async def handle_verack(self, peer_name, message_header, message):
        #pylint: disable=unused-argument
        """
        Handles Verack message.
        """
        print("="*31)
        print("A verack message was received!")
        print("="*31)
        if not self.send_per_peer.get(peer_name):
            genesis_block = 0x00000f79b700e6444665c4d090c9b8833664c4e2597c7087a6ba6391b956cc89
            print("Sending getheaders with genesis hash {}...".format(hex(genesis_block)))
            get_headers = GetHeaders([genesis_block])
            self.send_message(peer_name, get_headers)
            self.send_per_peer[peer_name] = True
            NODES[peer_name]["performance_time"] = time()
        print("="*31)

    # async def handle_inv(self, peer_name, message_header, message):
    #     #pylint: disable=unused-argument
    #     """
    #     Handles Inv message.
    #     """
    #     print("="*31)
    #     print("A inv message was received!")
    #     print("="*31)
    #     print(message.inventory)

    async def handle_headers(self, peer_name, message_header, message):
        #pylint: disable=unused-argument
        """
        Handles Headers message.
        """
        chunk_len = len(message.headers)
        blocks_num = self.blocks_num_per_peer.get(peer_name, 0)
        if not blocks_num:
            self.blocks_num_per_peer[peer_name] = 0
        self.blocks_num_per_peer[peer_name] += chunk_len
        last_hash = message.headers[-1].calculate_hash()
        if chunk_len < 2000:
            print("="*31)
            print(f"Last headers message from {peer_name} was received!")
            print("="*31)
            print("LEN:", len(message.headers))
            print("TOTAL:", blocks_num + chunk_len)
            print("OFFSET:", NODES[peer_name]["offset"])
            print("="*31)
            start_time = NODES[peer_name]["performance_time"]
            NODES[peer_name]["performance_time"] = time() - start_time
            last_timestamp = message.headers[-1].timestamp
            print(f"Download performance {NODES[peer_name]['performance_time']}")
            print(f"Received getheaders with hash {last_hash}")
            print(f"Received getheaders with timstamp {last_timestamp}")
            print("="*31)
            await self.close_connection(peer_name)
        else:
            get_headers = GetHeaders([int(last_hash, 16)])
            self.send_message(peer_name, get_headers)


if __name__ == "__main__":
    LOOP = get_event_loop()
    try:
        PINK_NODE = TestAddrNode("0.0.0.0", "9134")
        TASKS = [
            ensure_future(PINK_NODE.connect(v["ip"], v["port"])) for v in HARDCODED_NODES.values()
        ]
        LOOP.run_until_complete(gather(*TASKS))
    except KeyboardInterrupt:
        print("Caught keyboard interrupt. Canceling tasks...")
        # TODO: Handling tasks cancelation.
        # KeyboardInterrupt is not properly handled on Windows
        # Issue will be resolved in Python 3.8
    finally:
        pass

    # with open("network_nodes.json", "w+") as fp:
    #     json.dump(NODES, fp, sort_keys=True, indent=4)
