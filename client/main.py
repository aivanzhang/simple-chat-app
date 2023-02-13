import sys
import socket
import threading
import grpc
import time
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
use_grpc = True # TODO: turn this into command line argument

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



def main(host: str = "127.0.0.1", port: int = 3000) -> None:
    """
    Initializes and connects to the server.
    @Parameter:
    1. host: The host to connect to.
    2. port: The port to connect to.
    @Returns: None.
    """

    # gRPC implementation
    print(f"Starting connection to {host}:{port}")
    if(use_grpc):
        listen_thread = None
        with grpc.insecure_channel(f"{host}:{port}") as channel:
            stub = main_pb2_grpc.ChatterStub(channel)

            client_request_iterator = grpc_client_main_loop()

            # client listens for messages from other clients
            def listen():
                try:
                    for message in stub.Listen(main_pb2.Empty()):
                        print(message)
                except ValueError:
                    print("Shutting down.")
                except KeyboardInterrupt:
                    print("Shutting down.")
                return
            listen_thread = threading.Thread(target=(listen), args=())
            listen_thread.start()

            try:
                # client request and server response back-and-forth
                for server_response in stub.Chat(client_request_iterator):
                    print(server_response.message, flush = True)            

            except KeyboardInterrupt:
                listen_thread.join()
                return

            # TODO: does quit work? can use thread event to make sure quit is cancelling the listen thread
            listen_thread.join()
            return
    
    # Wire protocol implementation            
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

def grpc_client_main_loop():
    print("Enter username (will be created if it doesn't exist): ", flush = True)
    while True:
        username = input()
        if (not username):
            continue
        break

    yield main_pb2.UserRequest(action=Action.JOIN, username=username, message="")

    print("Actions: list, send <user>, delete <user>, quit", flush = True)

    while True:
        action = input("> ")
        
        action_list = action.split()

        if (len(action_list) == 0):
            continue
        
        elif (action_list[0] == "list"):
            
            yield main_pb2.UserRequest(action=action_list[0], username=username, message="")

        elif (action_list[0] == "send"):
            if (len(action_list) < 2):
                print("Must specify valid user to send to. Try again.", flush = True)
                continue
            print("Message to send to {user}?".format(user=' '.join(action_list[1:])))

            while True:
                message = input(">>> ")
                if (not message):
                    continue
                break

            yield main_pb2.UserRequest(action=action_list[0], username=' '.join(action_list[1:]), message=message)

        elif (action_list[0] == "delete"):
            if (len(action_list) != 2):
                print("Must specify valid user to delete. Try again.", flush = True)
                continue
            if (username == ' '.join(action_list[1:])):
                print("Cannot delete self user.", flush = True)
                continue
            
            yield main_pb2.UserRequest(action=action_list[0], username=' '.join(action_list[1:]), message="")

        elif (action_list[0] == "quit"):
            
            yield main_pb2.UserRequest(action=action_list[0], username=' '.join(action_list[1:]), message="")

        else:
            print("Unrecognized action.", flush = True)
            continue


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
                print(message[-1], flush = True)
            if (not respond_event.is_set() and message[1] == Action.RETURN):
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

    print("Actions: list, send <user>, delete <user>, quit", flush = True)

    while run_event.is_set():
        respond_event.clear()

        sys.stdout.flush()
        action = input("> ")

        action_list = action.split()

        if (len(action_list) == 0):
            continue

        if (action_list[0] == "list"):
            package(Action.LIST, [""], client_socket)
        
        elif (action_list[0] == "send"):
            if (len(action_list) < 2):
                print("Must specify valid user to send to. Try again.", flush = True)
                continue
            print("Message to send to {user}?".format(user=' '.join(action_list[1:])))

            while True:
                message = input(">>> ")
                if (not message):
                    continue
                break

            package(Action.SEND, [' '.join(action_list[1:]), message], client_socket)
        
        elif (action_list[0] == "delete"):
            if (len(action_list) != 2):
                print("Must specify valid user to delete. Try again.", flush = True)
                continue
            if (username == ' '.join(action_list[1:])):
                print("Cannot delete self user.", flush = True)
                continue
            package(Action.DELETE, [' '.join(action_list[1:])], client_socket)
        
        elif (action_list[0] == "quit"):
            run_event.clear()
        
        else:
            print("Unrecognized action.", flush = True)
            continue

        respond_event.wait() 

    return


if __name__ == '__main__':
    main()
