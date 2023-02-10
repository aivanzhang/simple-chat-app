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
use_grpc = False

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

    print(f"Starting connection to {host}:{port}")
    if(use_grpc):
        listen_thread = None
        with grpc.insecure_channel(f"{host}:{port}") as channel:
            stub = main_pb2_grpc.ChatterStub(channel)
            try:
                while True:
                    command = input("Command: ")
                    if command == "quit":
                        return
                    else:
                        response = stub.Chat(
                            main_pb2.UserRequest(action=command, username="ivan", message="HI")
                        )
                        print(response.message)
                    if command == "join":
                        def periodically_listen():
                            print("Listening to pending messages...")
                            while True:
                                time.sleep(2)
                                response = stub.ListenToPendingMessages(main_pb2.Empty())
                                if(not response.isEmpty):
                                    print(response.message)
                        listen_thread = threading.Thread(target=(periodically_listen), args=())
                        listen_thread.start()
            except KeyboardInterrupt:
                listen_thread.join()
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

    print("Actions: list, send <user>, delete <user>, quit:", flush = True)

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
