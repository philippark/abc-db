import socket
import selectors
import struct
import types

HOST = '0.0.0.0'
PORT = 1234

sel = selectors.DefaultSelector()

# helper functions for buffers

def buf_append(buf: bytearray, data: bytes):
    buf.extend(data)

def buf_consume(buf: bytearray, n: int):
    del buf[:n]

# Handle listening socket
def accept_wrapper(sock):
    conn, addr = sock.accept()
    conn.setblocking(False)

    data = types.SimpleNamespace(addr=addr,
                                 inb=bytearray(),
                                 outb=bytearray())
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn, events, data)

# Process buffered requests for a connection
def _process_requests(data):
    # protocol: 4-byte little-endian length prefix
    while True:
        if len(data.inb) < 4:
            break
        msg_len = struct.unpack_from('<I', data.inb)[0]
        if len(data.inb) < 4 + msg_len:
            break
        msg = bytes(data.inb[4 : 4 + msg_len])
        print(f"client says: len:{msg_len} data:{msg[:100].decode(errors='ignore')}")
        # echo response
        buf_append(data.outb, struct.pack('<I', msg_len))
        buf_append(data.outb, msg)
        buf_consume(data.inb, 4 + msg_len)

def service_connection(key, mask):
    sock = key.fileobj
    data = key.data

    if mask & selectors.EVENT_READ:
        try:
            recv_data = sock.recv(4096)
        except BlockingIOError:
            recv_data = b''
        if recv_data:
            buf_append(data.inb, recv_data)
            _process_requests(data)
        else:  # connection closed
            sel.unregister(sock)
            sock.close()
            return

    if mask & selectors.EVENT_WRITE and data.outb:
        try:
            sent = sock.send(data.outb)
            buf_consume(data.outb, sent)
        except BlockingIOError:
            pass

def start_server():
    # Create listening socket
    lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    lsock.bind((HOST, PORT))
    lsock.listen()

    # Register listening socket as a read event
    lsock.setblocking(False)
    sel.register(lsock, selectors.EVENT_READ, data=None)

    while True:
        events = sel.select(timeout=None)
        for key, mask in events:
            if key.data is None:  # listening socket
                accept_wrapper(key.fileobj)
            else:  # client socket
                service_connection(key, mask)

if __name__ == '__main__':
    start_server() 