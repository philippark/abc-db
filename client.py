import socket
import struct

HOST = 'localhost'
PORT = 1234

def buf_append(buf: bytearray, data: bytes):
    buf.extend(data)

def send_message(sock: socket.socket, payload: bytes) -> None:
    header = struct.pack('<I', len(payload))
    sock.sendall(header + payload)

def recv_message(sock: socket.socket) -> bytes | None:
    # first read exactly 4 bytes of length prefix
    header = bytearray()
    while len(header) < 4:
        chunk = sock.recv(4 - len(header))
        if not chunk:
            return None
        buf_append(header, chunk)
    msg_len = struct.unpack('<I', header)[0]

    # then read the body in a loop until complete
    data = bytearray()
    while len(data) < msg_len:
        chunk = sock.recv(msg_len - len(data))
        if not chunk:
            return None
        buf_append(data, chunk)
    return bytes(data)

def main():
    msgs = [b'hello', b'world', b'test']
    with socket.create_connection((HOST, PORT)) as sock:
        print(f'connected to {(HOST, PORT)}')
        for m in msgs:
            print('sending', m)
            send_message(sock, m)
            resp = recv_message(sock)
            if resp is None:
                print('connection closed')
                break
            print('received', resp)

if __name__ == '__main__':
    main()