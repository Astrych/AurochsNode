"""
Network peer implementation.
"""

from asyncio import open_connection, create_task, CancelledError

from .buffer import ProtocolBuffer


class Peer:
    """
    Network peer.
    """

    async def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.buffer = ProtocolBuffer()

        self.reader, self.writer = await open_connection(ip, port)

    async def close_connection(self):
        """
        Closes TCP connection and ensures it's closed.

        :param peer_name: Peer name
        """
        self.reader.feed_eof()
        self.writer.close()
