from utils import *
from const import *
import types
import socket
import selectors

socket_selector = selectors.DefaultSelector()


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
    sock.setblocking(False)
    socket_selector.register(
        sock, selectors.EVENT_READ | selectors.EVENT_WRITE, None
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
            for key, mask in socket_selector.select(timeout=None):
                if key.data is None:
                    accept_connection(key.fileobj)
                else:
                    service_connection(key.fileobj, key.data, mask)
    except KeyboardInterrupt:
        print("Exiting")
    finally:
        socket_selector.close()


def accept_connection(socket):
    """
    Accepts a connection.
    @Parameter: 
    1. socket: The socket to accept the connection on.   
    @Returns: None.
    """
    conn, addr = socket.accept()
    print(f"New connection arrived from {addr}")
    conn.setblocking(False)
    # socket_selector.register(
    #     conn, selectors.EVENT_READ | selectors.EVENT_WRITE, types.SimpleNamespace(
    #         addr=addr, inb=b"", outb=b"")
    # )


def service_connection(socket, data, mode):
    """
    Services a connection.
    @Parameter:
    1. socket: The socket to service.
    2. data: Data to read/write from the socket.
    3. mode: The mode to service the connection with.
    @Returns: None.
    """

    if mode & selectors.EVENT_READ:
        print(data)
        # recv_data = socket.recv(MAX_SOCKET_BUFFER_SIZE)
        # if recv_data:
        #     print(recv_data)
        # else:
        #     print(f"Closing connection to {data.addr}")
        #     socket_selector.unregister(socket)
        #     socket.close()
    if mode & selectors.EVENT_WRITE:
        print("Writing data")
        print(data)
        # if data.outb:
        #     print(f"Echoing {data.outb!r} to {data.addr}")
        #     sent = socket.send(data.outb)
        #     data.outb = data.outb[sent:]


init()
