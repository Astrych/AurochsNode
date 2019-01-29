import socket

from pinkcoin.clients import NetworkClient
from pinkcoin.serializers import GetAddr, GetHeaders
from pinkcoin.fields import INVENTORY_TYPE


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

    def handle_addr(self, message_header, message):
        print("===============================")
        print("A addr message was received!")
        print("===============================")
        print(message.addresses)
        print("LEN:", len(message.addresses))
        print("===============================")

    # def handle_message_header(self, message_header, payload):
    #     print("Received message:", message_header.command)

    def handle_verack(self, message_header, message):
        print("===============================")
        print("A verack message was received!")
        print("===============================")
        if not self.send:
            genesis_block = 106807621267983349431936820025262069513739093724410944266789304831233161
            print("Sending getheaders with hash {}...".format(hex(genesis_block)))
            get_headers = GetHeaders([genesis_block])
            self.send_message(get_headers)
            self.send = True
        print("===============================")

    def handle_inv(self, message_header, message):
        print("===============================")
        print("A inv message was received!")
        print("===============================")
        print(message.inventory)
        # if message.inventory[0].inv_type == INVENTORY_TYPE["MSG_BLOCK"] and not self.send:
        #     # block_hash = message.inventory[0].inv_hash
        #     genesis_block = 106807621267983349431936820025262069513739093724410944266789304831233161
        #     print("Sending getheaders with hash {}...".format(hex(genesis_block)))
        #     get_headers = GetHeaders([genesis_block])
        #     self.send_message(get_headers)
        #     self.send = True
        # print("===============================")

    def handle_headers(self, message_header, message):
        print("===============================")
        print("A headers message was received!")
        print("===============================")
        self.blocks_num += len(message.headers)
        print("LEN:", len(message.headers))
        print("TOTAL:", self.blocks_num)
        # count = 0
        # for header in message.headers:
        #     count += 1
        #     if count == len(message.headers) - 1: break
        #     print("version: {}".format(header.version))
        #     print("Hash: {}", header.calculate_hash())
        #     print("prev_block: {} - {}".format(header.prev_block, hex(header.prev_block)))
        #     print("merkle_root: {} - {}".format(header.merkle_root, hex(header.merkle_root)))
        #     print("timestamp: {}".format(header.timestamp))
        #     print("bits: {} - {}".format(header.bits, hex(header.bits)))
        #     print("nonce: {}".format(header.nonce))
        #     print("txns_count: {}".format(header.txns_count))
        #     print("sig: {}".format(header.sig))
        print("===============================")
        print("Sending getheaders with hash {}...".format(message.headers[-1].calculate_hash()))
        print("Sending getheaders with timstamp {}...".format(message.headers[-1].timestamp))
        get_headers = GetHeaders([int(message.headers[-1].calculate_hash(), 16)])
        self.send_message(get_headers)


node_address = "tokyo.pinkarmy.ml"
print(node_address)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((node_address, 9134))
client = PinkcoinClient(sock)

try:
    client.handshake()
    client.loop()
except KeyboardInterrupt:
    client.close_stream()
