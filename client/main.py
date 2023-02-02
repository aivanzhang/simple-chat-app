import sys
import socket
import selectors
from const import *
# Add the parent wire_protocol directory to the path so that its methods can be imported
# sys.path.append('..')
# from wire_protocol.protocol import encode, decode


client_selector = selectors.DefaultSelector()
messages = ["Message 1 from client.", "Message 2 from client."]


def init():
    """
    Initializes the client.
    @Parameter: None.
    @Returns: None.
    """
    connect_to_server()


def connect_to_server(host: str = "127.0.0.1", port: int = 3000) -> None:
    """
    Connects to the server.
    @Parameter:
    1. host: The host to connect to.
    2. port: The port to connect to.
    @Returns: None.
    """
    print(f"Starting connection to {host}:{port}")
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.setblocking(False)
    client_socket.connect_ex((host, port))
    client_selector.register(
        client_socket, selectors.EVENT_READ | selectors.EVENT_WRITE
    )
    start_listening()


def start_listening():
    """
    Starts listening for incoming connections.
    @Parameter: None.
    @Returns: None.
    """
    try:
        while True:
            for key, mask in client_selector.select(timeout=None):
                if key.data:
                    service_connection(key.fileobj, key.data, mask)
    except KeyboardInterrupt:
        print("Exiting")
    finally:
        client_selector.close()


def service_connection(socket, data, mode):
    if mode & selectors.EVENT_READ:
        recv_data = socket.recv(MAX_CLIENT_BUFFER_SIZE)
        if recv_data:
            print(recv_data)
        # if not recv_data or data.recv_total == data.msg_total:
        #     print(f"Closing connection {data.connid}")
        #     client_selector.unregister(socket)
        #     socket.close()
    if mode & selectors.EVENT_WRITE:
        print("Write mode")
        # if not data.outb and data.messages:
        #     data.outb = data.messages.pop(0)
        # if data.outb:
        #     print(f"Sending {data.outb!r} to connection {data.connid}")
        #     sent = socket.send(data.outb)  # Should be ready to write
        #     data.outb = data.outb[sent:]


init()
