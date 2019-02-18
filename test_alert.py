"""
Program connects to a peer and wait for alert message.
After receiving it payload is deserialized and printed.
"""

from asyncio import get_event_loop, ensure_future, gather
from io import BytesIO

from pinkcoin.node import Node
from pinkcoin.serializers import AlertPayloadSerializer


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

        await super().handle_version(peer_name, message_header, message)

    async def handle_alert(self, peer_name, message_header, message):
        #pylint: disable=unused-argument
        """
        Handles alert message.
        """
        print("An alert was received from", peer_name)
        print("payload as uchar[]", message.payload)
        print("signature", message.signature)

        # TODO: Check signature before deserialization.
        deserializer = AlertPayloadSerializer()
        alert = deserializer.deserialize(BytesIO(message.payload))

        print("version:", alert.version)
        print("relay_until:", alert.relay_until)
        print("expiration:", alert.expiration)
        print("id:", alert.alert_id)
        print("cancel:", alert.cancel)
        print("set_cancel:", alert.set_cancel)
        print("min_ver:", alert.min_ver)
        print("max_ver:", alert.max_ver)
        print("set_sub_ver:", alert.set_sub_ver)
        print("priority:", alert.priority)
        print("comment:", alert.comment)
        print("status_bar", alert.status_bar)
        print("reserved", alert.reserved)
        print("="*31)


if __name__ == "__main__":
    LOOP = get_event_loop()
    try:
        PINK_NODE = PinkcoinNode("0.0.0.0", "9134")
        TASKS = [
            ensure_future(PINK_NODE.connect("18.224.37.139", 9134))
        ]
        LOOP.run_until_complete(gather(*TASKS))
    except KeyboardInterrupt:
        print("Caught keyboard interrupt. Canceling tasks...")
        # TODO: Handling tasks cancelation.
        # KeyboardInterrupt is not properly handled on Windows
        # Issue will be resolved in Python 3.8
    finally:
        pass
