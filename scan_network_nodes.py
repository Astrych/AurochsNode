"""
Program connects to list of hardcoded nodes and asks them for
their peers. After that it uses these peers to repeat the process.
That way it builds list of all recently seen peers in the network.
"""

import json
from asyncio import get_event_loop, ensure_future, gather
from typing import Dict

from pinkcoin.node import Node
from pinkcoin.serializers import GetAddr
from pinkcoin.params import HARDCODED_NODES


NODES: Dict = {}

class PinkcoinNode(Node):
    """
    Specific node implementation handling
    fetchng list of nodes peers.
    """
    async def handle_version(self, peer_name, message_header, message):
        print("-"*31)
        print(f"A version message from {peer_name} was received!")
        print("-"*31)
        print(message.user_agent)
        print(message.version)
        print(message.addr_recv)
        print(message.addr_from)
        print("-"*31)

        if peer_name in NODES:
            NODES[peer_name]["version"] = message.version
            NODES[peer_name]["agent"] = message.user_agent.decode("utf-8")
        else:
            NODES[peer_name] = {
                "version": message.version,
                "agent": message.user_agent.decode("utf-8"),
            }

        await super().handle_version(peer_name, message_header, message)

    async def handle_message_header(self, peer_name, message_header, payload):
        print(f"Received {message_header.command} message from {peer_name}")
        if message_header.command == "verack":
            print(f"send getaddr to {peer_name}")
            getaddr = GetAddr()
            self.send_message(peer_name, getaddr)
        if message_header.command == "ping":
            print(f"send getaddr to {peer_name}")
            getaddr = GetAddr()
            self.send_message(peer_name, getaddr)

    async def handle_addr(self, peer_name, message_header, message):
        #pylint: disable=unused-argument
        """
        Handles Adrr message and store
        peers data in a dictionary.

        :param peer_name: Peer name
        :param message_header: The Version message header
        :param message: The Version message
        """
        print(f"A addr message was received from {peer_name}")
        peers_list = []
        for address in message.addresses:
            peers_list.append({
                "ip": address.ip_address,
                "port": address.port,
                "timestamp": address.timestamp,
                "services": address.services,
            })

        NODES[peer_name]["peers"] = peers_list
        print("Number of peers:", len(message.addresses))

        await self.close_connection(peer_name)


if __name__ == "__main__":
    LOOP = get_event_loop()
    try:
        PINK_NODE = PinkcoinNode("0.0.0.0", "9134")
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

    with open("network_nodes.json", "w+") as fp:
        json.dump(NODES, fp, sort_keys=True, indent=4)
