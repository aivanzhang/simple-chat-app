import sys
import socket
import threading
import grpc
# Add the parent wire_protocol directory to the path so that its methods can be imported
sys.path.append('..')
from wire_protocol.protocol import *
sys.path.append('../grpc_stubs')
import main_pb2, main_pb2_grpc

# Event that is set when threads are running and cleared when you want threads to stop
run_event = threading.Event()
# Event to block client UI until server response
respond_event = threading.Event()

# Client socket that connects to the server
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
use_grpc = True

def gracefully_shutdown():
    """
    Gracefully shuts down the client.
    @Parameter: None.
    @Returns: None.
    """
    # print("attempting to close socket and threads.")
    print("Shutting down.") # UI message
    run_event.clear()
    respond_event.set()
    try:
        client_socket.shutdown(socket.SHUT_RDWR)
    except OSError:
        # This occurs when the socket is already closed.
        pass
    global receive_thread, send_thread
    receive_thread.join()
    send_thread.join()
    # print("threads and socket successfully closed.")
    sys.exit(0)

def generate_messages(command, username, message="HI"):
    messages = [
        main_pb2.UserRequest(
            action=command,
            username=username,
            message=message
        ),
    ]
    for msg in messages:
        yield msg


def main(host: str = "127.0.0.1", port: int = 3000) -> None:
    """
    Initializes and connects to the server.
    @Parameter:
    1. host: The host to connect to.
    2. port: The port to connect to.
    @Returns: None.
    """

    print(f"Starting connection to {host}:{port}")
    if(use_grpc):
        with grpc.insecure_channel(f"{host}:{port}") as channel:
            stub = main_pb2_grpc.ChatterStub(channel)
            try:
                while True:
                    command = input("Command: ")
                    if command == "quit":
                        return
                    else:
                        responses = stub.Chat(generate_messages(command, "ivan"))
                        for response in responses:
                            print("Received message %s" %
                                (response.message))
            except KeyboardInterrupt:
                return
                
    else:
        client_socket.connect((host, port))
        run_event.set()
        respond_event.clear()
        global receive_thread, send_thread
        receive_thread = threading.Thread(
            target=client_receive, args=(client_socket,)
        )
        send_thread = threading.Thread(
            target=client_main_loop, args=(client_socket,)
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
            message = receive_unpkg_data(client_socket)
            if (message and len(message) > 2):
                print(message[-1], flush = True) # TODO: ordering of the messages is not yet enforced
            if (not respond_event.is_set()):
                respond_event.set()
        except ConnectionResetError:
            gracefully_shutdown()
        if (not message):
            run_event.clear()


def client_main_loop(client_socket):
    """
    Client UI main loop
    @Parameter:
    1. client_socket: The client socket to send messages to.
    @Returns: None.
    """
    print("Enter username (will be created if it doesn't exist): ", flush = True)
    while True:
        username = input()
        if (not username):
            continue
        break
    
    package("join", [username], client_socket)
    
    # block until server acks join
    respond_event.wait()

    while run_event.is_set():
        respond_event.clear() # TODO: a message from another user is not differentiated from the server's response to client's action

        print("Actions: list, send <user> <message>, delete <user>, quit:")
        action = input()

        action_list = action.split()

        if (len(action_list) == 0):
            continue

        if (action_list[0] == "list"):
            package(Action.LIST, [""], client_socket)
        
        elif (action_list[0] == "send"):
            if (len(action_list) < 2): # TODO: are we allowing spaces in username??
                print("Must specify user to send to. Try again.", flush = True)
                continue
            if (len(action_list) < 3):
                print("Must specify message to send. Try again.", flush = True)
                continue
            package(Action.SEND, action_list[1:], client_socket)
        
        elif (action_list[0] == "delete"):
            if (len(action_list) < 2): # TODO: are we allowing spaces in username??
                print("Must specify user to delete. Try again.", flush = True)
                continue
            if (username == action_list[1]):
                print("Cannot delete self user.", flush = True)
                continue
            package(Action.DELETE, action_list[1:], client_socket)
        
        elif (action_list[0] == "quit"):
            run_event.clear()
        
        else:
            print("Unrecognized action.", flush = True)
            continue

        respond_event.wait() 

    return


if __name__ == '__main__':
    main()
