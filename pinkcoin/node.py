"""Simple Pinkcoin full node implementation. Work in progress.
Right now only message protocol communication is implemented.
"""

import os
from io import BytesIO
from asyncio import open_connection, create_task, CancelledError

from .serializers import (
    MessageHeaderSerializer,
    Version,
    VerAck,
    Pong,
    MESSAGE_MAPPING,
)
from .exceptions import NodeDisconnectException, InvalidMessageChecksum


class ProtocolBuffer:
    """Buffer handling protocol messages.
    """
    def __init__(self):
        self.buffer = BytesIO()
        self.header_size = MessageHeaderSerializer.calcsize()

    def write(self, data):
        """Writes data to bytes buffer.
        """
        self.buffer.write(data)

    def receive_message(self):
        """Attempts to extract a header and message.
        It returns a tuple of (header, message) and sets whichever
        can be set so far (None otherwise).
        """
        # Calculates the size of the buffer.
        self.buffer.seek(0, os.SEEK_END)
        buffer_size = self.buffer.tell()

        # Checks if a complete header is present.
        if buffer_size < self.header_size:
            return (None, None)

        # Goes to the beginning of the buffer.
        self.buffer.seek(0)

        message_model = None
        message_header_serial = MessageHeaderSerializer()
        message_header = message_header_serial.deserialize(self.buffer)
        total_length = self.header_size + message_header.length

        # Incomplete message.
        if buffer_size < total_length:
            self.buffer.seek(0, os.SEEK_END)
            return (message_header, None)

        payload = self.buffer.read(message_header.length)
        remaining = self.buffer.read()
        self.buffer = BytesIO()
        self.buffer.write(remaining)
        payload_checksum = MessageHeaderSerializer.calc_checksum(payload)

        # Checks if the checksum is valid.
        if payload_checksum != message_header.checksum:
            msg = f"Bad checksum for command {message_header.command}"
            raise InvalidMessageChecksum(msg)

        if message_header.command in MESSAGE_MAPPING:
            deserializer = MESSAGE_MAPPING[message_header.command]()
            message_model = deserializer.deserialize(BytesIO(payload))

        return (message_header, message_model)


class Node:
    """The base class for a network node, this class
    implements utility functions to create your own class.

    :param ip: node ip address
    :param port: node port to it binds to
    """
    network_type = "main"

    def __init__(self, ip, port):
        self.node_ip = ip
        self.node_port = port
        # Peers connected to the node.
        self.peers = {}

    def send_message(self, peer_name, message):
        """Serializes the message using the appropriate
        serializer based on the message command
        and sends it to the socket stream.

        :param peer_name: Peer name
        :param message: The message object to send
        """
        try:
            writer = self.peers[peer_name]["writer"]
            writer.write(message.get_message(self.network_type))
        except KeyError:
            print(f"Error: Connection to {peer_name} doesn't exist.")

    async def close_connection(self, peer_name):
        """Closes TCP connection and ensures it's closed.

        :param peer_name: Peer name
        """
        try:
            writer = self.peers[peer_name]["writer"]
            writer.close()
            await writer.wait_closed()
            del self.peers[peer_name]
        except KeyError:
            print(f"Error: Connection to {peer_name} doesn't exist.")

    async def handle_message_header(self, peer_name, message_header, payload):
        """Is called for every message before the
        message payload deserialization.

        :param peer_name: Peer name
        :param message_header: The message header
        :param payload: The payload of the message
        """

    async def connect(self, peer_ip, peer_port):
        """Creates TCP connection and spawns new
        task handling communication.

        :param peer_ip: Peer ip address
        :param peer_port: Peer port
        """
        peer_name = f"{peer_ip}:{peer_port}"
        try:
            reader, writer = await open_connection(peer_ip, peer_port)
            self.peers[peer_name] = {
                "reader": reader,
                "writer": writer,
                "buffer": ProtocolBuffer()
            }
            client_coro = create_task(self.connection_handler(peer_name))
            await client_coro
        except CancelledError:
            print(f"Warning: Task handling connection to {peer_name} canceled.")
        except NodeDisconnectException:
            print(f"Warning: Peer {peer_name} disconnected")
            await self.close_connection(peer_name)
        except InvalidMessageChecksum as ex:
            print(f"Error: {ex} (node {peer_name}). Clossing connetion.")
            await self.close_connection(peer_name)
        except ConnectionError:
            print(f"Error: connection error for peer {peer_name}")

    async def connection_handler(self, peer_name):
        """Handles connection to the node's peer.
        """
        # Initialize communitaion.
        self.handshake(peer_name)
        try:
            writer = self.peers[peer_name]["writer"]
            # Enters connection read/write loop.
            while not writer.is_closing():
                await self.handle_message(peer_name)
        except KeyError:
            print(f"Error: Connection to {peer_name} doesn't exist.")

    async def handle_message(self, peer_name):
        """Handles one message received from the peer.

        :param peer_name: Peer name
        """
        try:
            reader = self.peers[peer_name]["reader"]
            buffer = self.peers[peer_name]["buffer"]
        except KeyError:
            print(f"Error: Connection to {peer_name} doesn't exist.")
            return

        data = await reader.read(1024*8)

        if not data:
            raise NodeDisconnectException(f"Node {peer_name} disconnected.")

        buffer.write(data)
        message_header, message = buffer.receive_message()

        if message_header is not None:
            await self.handle_message_header(peer_name, message_header, data)

        if not message:
            return

        # Executes proper message handler.
        handle_func_name = "handle_" + message_header.command
        handle_func = getattr(self, handle_func_name, None)
        if handle_func and callable(handle_func):
            await handle_func(peer_name, message_header, message)

    def handshake(self, peer_name):
        """Implements the handshake of a network
        protocol. It sends the Version message.

        :param peer_name: Peer name
        """
        version = Version()
        self.send_message(peer_name, version)

    async def handle_version(self, peer_name, message_header, message):
        #pylint: disable=unused-argument
        """Handles the Version message and sends
        a VerAck message when it receives the Version message.

        :param peer_name: Peer name
        :param message_header: The Version message header
        :param message: The Version message
        """
        verack = VerAck()
        self.send_message(peer_name, verack)

    async def handle_ping(self, peer_name, message_header, message):
        #pylint: disable=unused-argument
        """Handles the Ping message and answers every
        Ping message with a Pong message using the nonce received.

        :param peer_name: Peer name
        :param message_header: The header of the Ping message
        :param message: The Ping message
        """
        pong = Pong()
        pong.nonce = message.nonce
        self.send_message(peer_name, pong)
