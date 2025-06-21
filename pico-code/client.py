import usocket as socket
import ubinascii as binascii
import urandom as random
import ssl  # ✅ Updated import

from .protocol import Websocket, urlparse

class WebsocketClient(Websocket):
    is_client = True

def connect(uri):
    uri = urlparse(uri)
    assert uri

    sock = socket.socket()
    addr_info = socket.getaddrinfo(uri.hostname, uri.port)[0][-1]
    sock.connect(addr_info)

    if uri.protocol == 'wss':
        sock = ssl.wrap_socket(sock, server_hostname=uri.hostname)  # ✅ Updated wrapper

    def send_header(header, *args):
        sock.write((header % args) + '\r\n')

    key = binascii.b2a_base64(bytes([random.getrandbits(8) for _ in range(16)])).strip()

    send_header('GET %s HTTP/1.1', uri.path or '/')
    send_header('Host: %s:%s', uri.hostname, uri.port)
    send_header('Connection: Upgrade')
    send_header('Upgrade: websocket')
    send_header('Sec-WebSocket-Key: %s', key.decode())
    send_header('Sec-WebSocket-Version: 13')
    send_header('Origin: http://%s:%s' % (uri.hostname, uri.port))
    send_header('')

    # Skip HTTP response headers until an empty line
    while True:
        line = sock.readline()
        if not line or line == b'\r\n':
            break

    return WebsocketClient(sock)
