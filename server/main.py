import socket
import threading
import sys
from payload import *
from db_utils import save_db_to_disk
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


def gracefully_shutdown():
    """
    Gracefully shuts down the server.
    @Parameter: None.
    @Returns: None.
    """
    print("saving data to disk.")
    save_db_to_disk()
    print("attempting to close sockets and threads.")
    run_event.clear()
    try:
        for (client_socket, thread) in list(users_connections.values()):
            client_socket.shutdown(socket.SHUT_RDWR)
            thread.join()
    except (OSError):
        # This occurs when the socket is already closed.
        pass
    global sock
    sock.close()
    print("threads and sockets successfully closed.")
    sys.exit(0)


def gracefully_quit(username):
    """
    Gracefully removes a specific user from the server.
    @Parameter: None.
    @Returns: None.
    """
    if (not username):
        return
    print(f"attempting to close socket and thread for {username}.")
    user_socket, _ = users_connections[username]
    try:
        if (user_socket):
            user_socket.shutdown(socket.SHUT_RDWR)
    except OSError:
        # This occurs when the socket is already closed.
        pass
    del users_connections[username]
    print(f"threads and sockets successfully closed for {username}.")
    sys.exit(0)


def main(host: str = "127.0.0.1", port: int = 3000) -> None:
    """
    Initializes the server.
    @Parameter: None.
    @Returns: None.
    """
    init_db()
    init_users()
    global sock
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((host, port))
    sock.listen()
    run_event.set()
    print(f"Now listening on {host}:{port}")
    listen_for_connections(sock)


def handle_client(client_socket):
    username = None
    while run_event.is_set():
        message = receive_unpkg_data(client_socket)
        if (not message):
            gracefully_quit(username)
            return
        if (message[1] == Action.JOIN):
            username = message[2]
            users_connections[username] = (
                client_socket, threading.current_thread()
            )
        elif (message[1] == Action.QUIT):
            gracefully_quit(username)
            return
        response = (None, None)
        if (message[1] == Action.SEND):
            response = handle_send(message, username, users_connections)
        else:
            response = handle_payload(message)
            if (response[1]):
                package(Action.RETURN, [response[1]], client_socket)
            if (message[1] == Action.JOIN):
                send_pending_msgs(client_socket, username)


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
            thread = threading.Thread(
                target=handle_client, args=(client_socket,))
            thread.start()
    # This includes KeyboardInterrupt (i.e. Control + C) and other errors
    except:
        gracefully_shutdown()


main()
