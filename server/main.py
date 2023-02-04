from utils import *
from const import *
import socket
import threading
import sys
# Add the parent wire_protocol directory to the path so that its methods can be imported
sys.path.append('..')
from wire_protocol.protocol import *


"""
`users_connections` is a global dictionary that stores the user connections data.
The key is the username of the user and the value is a tuple in the form 
(user's respective socket, thread running the socket). So for example, 
if the user "bob" has socket `socket1` running on thread `thread1`, then 
`users_connections` will be:
{
    "bob": (socket1, thread1)
}
"""
users_connections = {}
# Event that is set when threads are running and cleared when you want threads to stop
run_event = threading.Event()
# List of running threads
running_threads = []
# List of running sockets
running_sockets = []


def gracefully_shutdown():
    """
    Gracefully shuts down the server.
    @Parameter: None.
    @Returns: None.
    """
    print("attempting to close sockets and threads.")
    run_event.clear()
    try:
        for client_socket in running_sockets:
            client_socket.shutdown(socket.SHUT_RDWR)
    except OSError:
        # This occurs when the socket is already closed.
        pass
    for thread in running_threads:
        thread.join()
    print("threads and sockets successfully closed.")
    sys.exit(0)


def main(host: str = "127.0.0.1", port: int = 3000) -> None:
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
    run_event.set()
    print(f"Now listening on {host}:{port}")
    listen_for_connections(sock)


def handle_client(client_socket):
    while run_event.is_set():
        # print("Handling client...")
        message = client_socket.recv(1024)
        if (not message):
            # TODO handle client disconnect
            return
            # print(message)


def listen_for_connections(sock: socket.socket):
    """
    Listens for connections from clients and attach them to individual threads.
    @Parameter:
    1. sock: The socket to listen for connections.
    @Returns: None.
    """
    try:
        print("Server is listening and accepting connections...")
        while True:
            client_socket, client_address = sock.accept()
            print(f'New connection from {client_address}')
            running_sockets.append(client_socket)
            client_socket.send('You are now connected!'.encode('utf-8'))
            thread = threading.Thread(
                target=handle_client, args=(client_socket,))
            thread.start()
            running_threads.append(thread)
    except KeyboardInterrupt:
        gracefully_shutdown()


main()
