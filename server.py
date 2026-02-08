import socket
import sys

HOST = '0.0.0.0'
PORT = 1234

def handle_request(conn, data):
    # read request
    msg = data.decode()
    print(f'client says: {msg}')

    # send response
    response = 'world'
    conn.sendall(response.encode())

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        s.bind((HOST, PORT))
        s.listen()

        while True:
            conn, addr = s.accept()

            print('connected by', addr)
            with conn:
                while True:
                    data = conn.recv(1024)
                    if not data:
                        print('client disconnected')
                        break

                    handle_request(conn, data)

if __name__ == '__main__':
    start_server() 