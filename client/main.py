from wire_protocol.protocol import *
import sys
import socket
import threading
from const import *
# Add the parent wire_protocol directory to the path so that its methods can be imported
sys.path.append('..')


def init(host: str = "127.0.0.1", port: int = 3000) -> None:
    """
    Initializes and connects to the server.
    @Parameter:
    1. host: The host to connect to.
    2. port: The port to connect to.
    @Returns: None.
    """

    print(f"Starting connection to {host}:{port}")
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
    threading.Thread(target=client_receive, args=(client_socket,)).start()
    threading.Thread(target=client_send, args=(client_socket,)).start()


def client_receive(client_socket):
    while True:
        try:
            message = client_socket.recv(
                MAX_CLIENT_BUFFER_SIZE).decode('utf-8')
            if decode(message).TYPE == Actions.CREATE:
                client_socket.send(username.encode('utf-8'))
            else:
                print(message)
        except:
            print('Error!')
            client_socket.close()
            break

# JY: I will add to this thread to make it client's main loop, which covers send and all the other available actions
def client_send(client_socket):
    while True:
        message = f'{username}: {input("")}'
        client_socket.send(message.encode('utf-8'))


init()
