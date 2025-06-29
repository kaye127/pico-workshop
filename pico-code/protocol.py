import ure as re
import ustruct as struct
import urandom as random
import usocket as socket
from ucollections import namedtuple

# Opcodes
OP_CONT = const(0x0)
OP_TEXT = const(0x1)
OP_BYTES = const(0x2)
OP_CLOSE = const(0x8)
OP_PING = const(0x9)
OP_PONG = const(0xa)

# Close codes
CLOSE_OK = const(1000)
CLOSE_GOING_AWAY = const(1001)
CLOSE_PROTOCOL_ERROR = const(1002)
CLOSE_DATA_NOT_SUPPORTED = const(1003)
CLOSE_BAD_DATA = const(1007)
CLOSE_POLICY_VIOLATION = const(1008)
CLOSE_TOO_BIG = const(1009)
CLOSE_MISSING_EXTN = const(1010)
CLOSE_BAD_CONDITION = const(1011)

URL_RE = re.compile(r'(wss|ws)://([A-Za-z0-9\-\.]+)(?:\:([0-9]+))?(/.+)?')
URI = namedtuple('URI', ('protocol', 'hostname', 'port', 'path'))

class NoDataException(Exception):
    pass

class ConnectionClosed(Exception):
    pass

def urlparse(uri):
    match = URL_RE.match(uri)
    if match:
        protocol = match.group(1)
        host = match.group(2)
        port = match.group(3)
        path = match.group(4)

        if protocol == 'wss':
            port = int(port or 443)
        elif protocol == 'ws':
            port = int(port or 80)
        else:
            raise ValueError('Invalid scheme %s' % protocol)

        return URI(protocol, host, port, path)

class Websocket:
    is_client = False

    def __init__(self, sock):
        self.sock = sock
        self.open = True

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()

    def settimeout(self, timeout):
        self.sock.settimeout(timeout)

    def read_frame(self, max_size=None):
        two_bytes = self.sock.read(2)
        if not two_bytes:
            raise NoDataException
        byte1, byte2 = struct.unpack('!BB', two_bytes)

        fin = bool(byte1 & 0x80)
        opcode = byte1 & 0x0f

        mask = bool(byte2 & (1 << 7))
        length = byte2 & 0x7f

        if length == 126:
            length, = struct.unpack('!H', self.sock.read(2))
        elif length == 127:
            length, = struct.unpack('!Q', self.sock.read(8))

        if mask:
            mask_bits = self.sock.read(4)

        try:
            data = self.sock.read(length)
        except MemoryError:
            self.close(code=CLOSE_TOO_BIG)
            return True, OP_CLOSE, None

        if mask:
            data = bytes(b ^ mask_bits[i % 4] for i, b in enumerate(data))

        return fin, opcode, data

    def write_frame(self, opcode, data=b''):
        fin = True
        mask = self.is_client
        length = len(data)

        byte1 = 0x80 if fin else 0
        byte1 |= opcode

        byte2 = 0x80 if mask else 0

        if length < 126:
            byte2 |= length
            self.sock.write(struct.pack('!BB', byte1, byte2))
        elif length < (1 << 16):
            byte2 |= 126
            self.sock.write(struct.pack('!BBH', byte1, byte2, length))
        elif length < (1 << 64):
            byte2 |= 127
            self.sock.write(struct.pack('!BBQ', byte1, byte2, length))
        else:
            raise ValueError()

        if mask:
            mask_bits = struct.pack('!I', random.getrandbits(32))
            self.sock.write(mask_bits)
            data = bytes(b ^ mask_bits[i % 4] for i, b in enumerate(data))

        self.sock.write(data)

    def recv(self):
        assert self.open

        while self.open:
            try:
                fin, opcode, data = self.read_frame()
            except NoDataException:
                return ''
            except ValueError:
                self._close()
                raise ConnectionClosed()

            if not fin:
                raise NotImplementedError()

            if opcode == OP_TEXT:
                return data.decode('utf-8')
            elif opcode == OP_BYTES:
                return data
            elif opcode == OP_CLOSE:
                self._close()
                return
            elif opcode == OP_PONG:
                continue
            elif opcode == OP_PING:
                self.write_frame(OP_PONG, data)
                continue
            elif opcode == OP_CONT:
                raise NotImplementedError(opcode)
            else:
                raise ValueError(opcode)

    def send(self, buf):
        assert self.open

        if isinstance(buf, str):
            opcode = OP_TEXT
            buf = buf.encode('utf-8')
        elif isinstance(buf, bytes):
            opcode = OP_BYTES
        else:
            raise TypeError()

        self.write_frame(opcode, buf)

    def close(self, code=CLOSE_OK, reason=''):
        if not self.open:
            return

        buf = struct.pack('!H', code) + reason.encode('utf-8')
        self.write_frame(OP_CLOSE, buf)
        self._close()

    def _close(self):
        self.open = False
        self.sock.close()
