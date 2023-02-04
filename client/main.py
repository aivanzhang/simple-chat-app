import sys
import socket
import threading
from const import *
# Add the parent wire_protocol directory to the path so that its methods can be imported
sys.path.append('..')
from wire_protocol.protocol import *

# Checks if server returned a message confirming the connection
got_connection_confirmation = False
# Event that is set when threads are running and cleared when you want threads to stop
run_event = threading.Event()
# Client socket that connects to the server
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def gracefully_shutdown():
    """
    Gracefully shuts down the client.
    @Parameter: None.
    @Returns: None.
    """
    print("attempting to close socket and threads.")
    run_event.clear()
    try:
        client_socket.shutdown(socket.SHUT_RDWR)
    except OSError:
        # This occurs when the socket is already closed.
        pass
    global receive_thread, send_thread
    receive_thread.join()
    send_thread.join()
    print("threads and socket successfully closed.")
    sys.exit(0)


def main(host: str = "127.0.0.1", port: int = 3000) -> None:
    """
    Initializes and connects to the server.
    @Parameter:
    1. host: The host to connect to.
    2. port: The port to connect to.
    @Returns: None.
    """

    print(f"Starting connection to {host}:{port}")
    client_socket.connect((host, port))
    run_event.set()
    global receive_thread, send_thread
    receive_thread = threading.Thread(
        target=client_receive, args=(client_socket,)
    )
    send_thread = threading.Thread(
        target=client_send, args=(client_socket,)
    )
    receive_thread.start()
    send_thread.start()
    try:
        while True and run_event.is_set():
            pass
    except KeyboardInterrupt:
        gracefully_shutdown()
    gracefully_shutdown()


def client_receive(client_socket):
    """
    Receives messages from the server and executes the respecitve action
    @Parameter:
    1. client_socket: The client socket to receive messages from.
    @Returns: None.
    """
    while run_event.is_set():
        try:
            message = client_socket.recv(
                MAX_CLIENT_BUFFER_SIZE
            ).decode('utf-8')
        except ConnectionResetError:
            gracefully_shutdown()
        if (not message):
            run_event.clear()
        print(message)


def client_send(client_socket):
    """
    Sends messages to the server given user input.
    @Parameter:
    1. client_socket: The client socket to send messages to.
    @Returns: None.
    """
    # JY: I will add to this thread to make it client's main loop, which covers send and all the other available actions
    while run_event.is_set():
        if (not got_connection_confirmation):
            continue
        message = input("Send a message: ")
        client_socket.send(message.encode('utf-8'))


if __name__ == '__main__':
    main()
