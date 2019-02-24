"""
Defines buffers handling protocol messages.
"""

import os
from io import BytesIO

from .base_serializer import MessageHeaderSerializer
from .messages import MESSAGE_MAPPING
from .exceptions import InvalidMessageChecksum


class ProtocolBuffer:
    """
    Buffer handling protocol messages.
    """
    def __init__(self):
        self.buffer = BytesIO()
        self.header_size = MessageHeaderSerializer.calcsize()

    def write(self, data):
        """
        Writes data to bytes buffer.
        """
        self.buffer.write(data)

    def receive_message(self):
        """
        Attempts to extract a header and message.
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
        # https://bitcoin.stackexchange.com/questions/22882/what-is-the-function-of-the-payload-checksum-field-in-the-bitcoin-protocol
        if payload_checksum != message_header.checksum:
            msg = f"Bad checksum for command {message_header.command}"
            raise InvalidMessageChecksum(msg)

        if message_header.command in MESSAGE_MAPPING:
            deserializer = MESSAGE_MAPPING[message_header.command]()
            message_model = deserializer.deserialize(BytesIO(payload))

        return (message_header, message_model)
