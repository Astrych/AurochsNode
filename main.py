import socket

from protocoin.clients import NetworkClient
from protocoin.serializers import GetAddr


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

    # def handle_alert(self, message_header, message):
    #     print("An alert was received!")
    #     print("version:", message.alert_info.version)
    #     print("relay_until:", message.alert_info.relay_until)
    #     print("expiration:", message.alert_info.expiration)
    #     print("id:", message.alert_info.id)
    #     print("cancel:", message.alert_info.cancel)
    #     print("set_cancel:", message.alert_info.set_cancel)
    #     print("min_ver:", message.alert_info.min_ver)
    #     print("max_ver:", message.alert_info.max_ver)
    #     print("set_sub_ver:", message.alert_info.set_sub_ver)
    #     print("priority:", message.alert_info.priority)
    #     print("comment:", message.alert_info.comment)
    #     print("status_bar", message.alert_info.status_bar)
    #     print("reserved", message.alert_info.reserved)
    #     # print("payload", message.payload)
    #     print("signature", message.signature)
    #     print("===================")

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
sock.connect(("127.0.0.1", 9134))
client = PinkcoinClient(sock)

try:
    client.handshake()
    client.loop()
except KeyboardInterrupt:
    client.close_stream()
