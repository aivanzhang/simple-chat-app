import sys
# Add the parent wire_protocol directory to the path so that its methods can be imported
sys.path.append('..')
from wire_protocol.protocol import *
from db_utils import *


def handle_payload(payload: "list[str]"):
    """
    Handles the incoming payload generated from client socket message.
    @Parameter:
    1. payload: The payload to handle. See wire_protocol/protocol.py Action class for more details on the payload.
    @Returns: A tuple with the following values
    (return value from database function (None if action isn't supported), message to send back to client that may be None)
    """
    payload = payload[1:]  # ignore the first count parameter
    if (payload[0] == Action.JOIN):
        # TODO handle returning pending messages
        success = create_user(payload[1])
        return (success, "User created successfully. Welcome!" if success else "Welcome back!")
    elif (payload[0] == Action.LIST):
        users = list_users()
        return (users, ", ".join(users))
    elif (payload[0] == Action.DELETE):
        return (delete_user(payload[1]), "User deleted successfully.")
    else:
        return (None, None)


def send_pending_msgs(client_socket, username):
    """
    Sends all pending messages to the client socket.
    @Parameter:
    1. client_socket: The client socket to send the messages to.
    2. username: The username of the client.
    @Returns: None
    """
    pending_messages = "\n".join(return_pending_messages(username))
    package(Action.RETURN, [pending_messages], client_socket)


def handle_send(payload, sender, online_users):
    """
    Handles the send action. Sends message from sender to receiver. Online users is a dictionary of online users 
    (see global user_connections in server/main.py).
    @Parameter:
    1. sender: The sender of the message.
    2. payload: The payload to handle. See wire_protocol/protocol.py Action class for more details on the payload.
    3. online_users: A dictionary of online users.
    @Returns: A tuple with the following values (True, "Message sent successfully.") if the user is online otherwise
    (False, "Message has been queued."). Note that this method sends the message to the receiver socket if they are online.
    """
    payload = payload[2:]
    receiver = payload[0]
    message = payload[1]
    message = f"{sender} says: {message}"
    if (user_exists(receiver)):
        if (receiver in online_users):
            package(Action.SEND, [message], online_users[receiver][0])
            package(Action.SEND, ["Message sent successfully."], online_users[sender][0]) # confirm to sender
            return (True, "Message sent successfully.")
        else:
            add_pending_message(receiver, message)
            package(Action.SEND, ["Message has been queued."], online_users[sender][0]) # confirm to sender
            return (False, "Message has been queued.")
    else:
        package(Action.SEND, ["The receipient does not exist."], online_users[sender][0]) # confirm to sender
        return (False, "The receipient does not exist.")
    
def handle_send_grpc(sender, receiver, message):
    message = f"{sender} says: {message}"
    if(user_exists(receiver)):
        add_pending_message(receiver, message)
        return "Message sent successfully."
    else:
        return "The receipient does not exist."