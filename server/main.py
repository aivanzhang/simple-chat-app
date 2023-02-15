import socket
import threading
import sys
from payload import *
from db_utils import save_db_to_disk
from concurrent import futures

import grpc
# Add the parent wire_protocol directory to the path so that its methods can be imported
sys.path.append('..')
from wire_protocol.protocol import * 
sys.path.append('../grpc_stubs')
import main_pb2, main_pb2_grpc

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

# gRPC implementation
class Chatter(main_pb2_grpc.ChatterServicer):
    def __init__(self):
        pass

    # client <> client communication
    def ListenToPendingMessages(self, request, context):
        pending_messages = return_pending_messages(request.username)
        return main_pb2.PendingMsgsResponse(message = "\n".join(pending_messages), isEmpty = len(pending_messages) == 0)

    # client <> server communication
    def Chat(self, request, context):
        action = request.action
        
        if(action == Action.LIST):
            payload = [None, action]
            return main_pb2.UserReply(message = handle_payload(payload)[1])
        
        elif(action == Action.DELETE):
            if (request.username in users_connections.keys()):
                return main_pb2.UserReply(message = "Cannot delete logged in user.")

            payload = [None, action, request.username]
            return main_pb2.UserReply(message = handle_payload(payload)[1])
        
        elif(action == Action.SEND):
            message = handle_send_grpc(request.username, request.recipient, request.message)
            return main_pb2.UserReply(message = message)
        
        elif(action == Action.JOIN):
            if (request.username in users_connections.keys()): # already logged in, refuse client
                return main_pb2.UserReply(message = "Already logged in elsewhere.")

            users_connections[request.username] = None
            return main_pb2.UserReply(message = handle_payload([None, "join", request.username])[1])
        
        elif(action == Action.QUIT):
            del users_connections[request.username]
            return main_pb2.UserReply(message = "")


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
    # undefined behavior if client and server mismatch on use_grpc
    global use_grpc
    use_grpc = False
    if ('--use_grpc' in sys.argv):
        use_grpc = True
    if ('--use_aws' in sys.argv):
        host = "0.0.0.0"

    init_db()
    init_users()

    if (use_grpc):
        try:
            server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
            main_pb2_grpc.add_ChatterServicer_to_server(Chatter(), server)
            server.add_insecure_port(f"{host}:{port}")
            server.start()
            print(f"Now listening on {host}:{port}")
            server.wait_for_termination()
        except KeyboardInterrupt:
            server.stop(0)
            print("saving data to disk.")
            save_db_to_disk()
        return
    else:
        global sock
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((host, port))
        sock.listen()
        run_event.set()
        print(f"Now listening on {host}:{port}")
        listen_for_connections(sock)


def handle_client(client_socket):
    """
    Handles client requests in non-grpc version.
    @Parameter:
    1. client_socket: The socket which connects to the client.
    @Returns: None.
    """
    username = None
    while run_event.is_set():
        message = receive_unpkg_data(client_socket)
        if (not message):
            gracefully_quit(username)
            return
        if (message[1] == Action.JOIN):
            username = message[2]
            if (username in users_connections.keys()): # already logged in, refuse client
                package(Action.RETURN, ["Already logged in elsewhere."], client_socket)
                client_socket.shutdown(socket.SHUT_RDWR)
                return

            users_connections[username] = (
                client_socket, threading.current_thread()
            )
        elif (message[1] == Action.QUIT):
            gracefully_quit(username)
            return
        response = (None, None)
        if (message[1] == Action.SEND):
            response = handle_send(message, username, users_connections)
        elif (message[1] == Action.DELETE and message[2] in users_connections.keys()):
            package(Action.RETURN, ["Cannot delete logged in user."], client_socket)
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
