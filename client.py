import socket
import sys

HOST = 'localhost'
PORT = 1234

def start_client():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(b'Hello')
        data = s.recv(1024)

        print(f'Recieved {data.decode()}')

if __name__ == '__main__':
    start_client()