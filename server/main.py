from utils import *
from const import *
import socket
import threading


"""
`users_connections` is a global dictionary that stores the user connections data. 
The key is the username of the user and the value is the user's respective socket. 
So for example, if the user "bob" has socket `socket1`, then `users_connections` will be:
{
    "bob": socket1
}
"""
users_connections = {}


def init(host: str = "127.0.0.1", port: int = 3000) -> None:
    """
    Initializes the server.
    @Parameter: None.   
    @Returns: None.
    """
    init_db()
    init_users()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((host, port))
    sock.listen()
    print(f"Now listening on {host}:{port}")
    listen_for_connections(sock)


def handle_client(username):
    while True:
        try:
            message = users_connections[username].recv(1024)
            print(message)
        except:
            break


def listen_for_connections(sock: socket.socket):
    while True:
        print("Server is listening and accepting connections...")
        client_socket, client_address = sock.accept()
        print(f'New connection from {client_address}')
        client_socket.send('What is your username?\n'.encode('utf-8'))
        username = client_socket.recv(MAX_SOCKET_BUFFER_SIZE)
        users_connections[username] = client_socket
        print(f'The username of this client is {username}'.encode('utf-8'))
        client_socket.send('You are now connected!'.encode('utf-8'))
        thread = threading.Thread(target=handle_client, args=(username,))
        thread.start()


init()
