import socket

from pinkcoin.clients import NetworkClient
from pinkcoin.serializers import GetAddr, GetHeaders
from pinkcoin.fields import INVENTORY_TYPE


class PinkcoinClient(NetworkClient):

    def handle_version(self, message_header, message):
        print("===============================")
        print("A version message was received!")
        print("===============================")
        print(message.user_agent)
        print(message.version)
        print(message.addr_recv)
        print(message.addr_from)
        print("===============================")
        super().handle_version(message_header, message)

    def handle_addr(self, message_header, message):
        print("===============================")
        print("A addr message was received!")
        print("===============================")
        print(message.addresses)
        print("LEN:", len(message.addresses))
        print("===============================")

    def handle_message_header(self, message_header, payload):
        print("Received message:", message_header.command)
        if message_header.command == "verack":
            print("send getaddr")
            getaddr = GetAddr()
            self.send_message(getaddr)
        if message_header.command == "ping":
            print("send getaddr")
            getaddr = GetAddr()
            self.send_message(getaddr)


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(("159.203.35.83", 19134))
client = PinkcoinClient(sock)

try:
    client.handshake()
    client.loop()
except KeyboardInterrupt:
    client.close_stream()
