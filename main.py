import socket

from pinkcoin.clients import NetworkClient
from pinkcoin.serializers import GetAddr, GetHeaders
from pinkcoin.fields import INVENTORY_TYPE


hardcoded_nodes = {
    "tokyo.pinkarmy.ml": "45.32.49.237",
    "sydney.pinkarmy.ml": "45.76.125.31",
    "singapore.pinkarmy.ml": "45.77.36.238",
    "paris.pinkarmy.ml": "217.69.6.86",
    "frankfurt.pinkarmy.ml": "95.179.165.154",
    "primary": "159.203.20.96"
}

nodes = {}

class PinkcoinClient(NetworkClient):

    def __init__(self, sock):
        super().__init__(sock)
        self.send = False
        self.blocks_num = 0

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

    def handle_verack(self, message_header, message):
        print("===============================")
        print("A verack message was received!")
        print("===============================")
        if not self.send:
            genesis_block = 106807621267983349431936820025262069513739093724410944266789304831233161
            print("Sending getheaders with genesis hash {}...".format(hex(genesis_block)))
            get_headers = GetHeaders([genesis_block])
            self.send_message(get_headers)
            self.send = True
        print("===============================")

    def handle_inv(self, message_header, message):
        print("===============================")
        print("A inv message was received!")
        print("===============================")
        print(message.inventory)

    def handle_headers(self, message_header, message):
        if self.blocks_num <= 729680:
            self.blocks_num += len(message.headers)
            last_hash = message.headers[-1].calculate_hash()
            last_timestamp = message.headers[-1].timestamp
            if self.blocks_num > 720000:
                print("===============================")
                print("A headers message was received!")
                print("===============================")
                print("LEN:", len(message.headers))
                print("TOTAL:", self.blocks_num)
                print("===============================")
                print(f"Sending getheaders with hash {last_hash}")
                print(f"Sending getheaders with timstamp {last_timestamp}")
            get_headers = GetHeaders([int(last_hash, 16)])
            self.send_message(get_headers)
        else:
            self.close_stream()


for dns_address, ip_address in hardcoded_nodes.items():
    print(dns_address)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip_address, 9134))
    client = PinkcoinClient(sock)

    try:
        client.handshake()
        client.loop()
    except KeyboardInterrupt:
        client.close_stream()
