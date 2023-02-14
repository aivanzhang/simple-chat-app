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

def gracefully_shutdown():
    """
    Gracefully shuts down the client for non-grpc version.
    @Parameter: None.
    @Returns: None.
    """
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
    # undefined behavior if client and server mismatch on use_grpc
    global use_grpc
    use_grpc = False
    if ('--use_grpc' in sys.argv):
        use_grpc = True

    # gRPC implementation
    print(f"Starting connection to {host}:{port}")
    if(use_grpc):
        listen_thread = None
        with grpc.insecure_channel(f"{host}:{port}") as channel:
            stub = main_pb2_grpc.ChatterStub(channel)

            print("Enter username (will be created if it doesn't exist): ", flush = True)
            while True:
                username = input()
                if (not username):
                    continue
                break

            response = stub.Chat(
                main_pb2.UserRequest(action="join", username=username, recipient="", message="")
            )
            print(response.message, flush = True)

            # user logged in elsewhere, end client
            if ('Already logged in' in response.message):
                return

            def periodically_listen():
                print("Listening to pending messages...")
                try:
                    while True:
                        time.sleep(2)
                        response = stub.ListenToPendingMessages(main_pb2.UserRequest(action='', username=username, recipient='', message=""))
                        if(not response.isEmpty):
                            print(response.message)
                except ValueError:
                    print("Shutting down.")
                except KeyboardInterrupt:
                    print("Shutting down.")
                return

            listen_thread = threading.Thread(target=(periodically_listen), args=())
            listen_thread.start()

            print("Actions: list, send <user>, delete <user>, quit", flush = True)

            try:
                while True:
                    action = input("> ")
                    
                    action_list = action.split()

                    if (len(action_list) == 0):
                        continue
                    
                    elif (action_list[0] == "list"):
                        response = stub.Chat(
                            main_pb2.UserRequest(action=action_list[0], username=username, recipient='', message="")
                        )

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

                        response = stub.Chat(
                            main_pb2.UserRequest(action=action_list[0], username=username, recipient=' '.join(action_list[1:]), message=message)
                        )

                    elif (action_list[0] == "delete"):
                        if (len(action_list) != 2):
                            print("Must specify valid user to delete. Try again.", flush = True)
                            continue
                        if (username == ' '.join(action_list[1:])):
                            print("Cannot delete self user.", flush = True)
                            continue
                        response = stub.Chat(
                            main_pb2.UserRequest(action=action_list[0], username=' '.join(action_list[1:]), recipient='', message="")
                        )

                    elif (action_list[0] == "quit"):
                        response = stub.Chat(
                            main_pb2.UserRequest(action=action_list[0], username=username, recipient='', message="")
                        )
                        return

                    else:
                        print("Unrecognized action.", flush = True)
                        continue

                    print(response.message, flush = True)

            except KeyboardInterrupt:
                # send quit to server
                response = stub.Chat(
                    main_pb2.UserRequest(action="quit", username=username, recipient='', message="")
                )
                listen_thread.join()
                return

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
