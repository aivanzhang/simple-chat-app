from enum import Enum
from wire_protocol.const import *


class Action(str, Enum):
    """
    Actions that can be performed by the client and server.
    """
    """
    User connects to server
    content:
    1. username: str
    """
    JOIN = "join",
    """
    List all users
    content: None
    """
    LIST = "list",
    """
    Send a message to username.
    content:
    1. username: str
    1. message: str
    """
    SEND = "send",
    """
    Deletes a user.
    content:
    1. username: str
    """
    DELETE = "delete",
    """
    Return value from client socket call
    content:
    1. return_value: str
    """
    RETURN = "return",
    """
    User exits to server
    content: None
    """
    QUIT = "quit",


SEPARATOR = "~$#"


def package(action: Action, payload: 'list[str]', socket=None):
    """
    Packages the data to be sent between the server and the client.
    @Parameter:
    1. action: The action to be performed.
    2. content: The payload to be sent. This is a list of strings with
    ordered parameters as specified in the Actions enum.
    3. socket: Socket to send the message to. If None, the message is not sent.
    @Returns: None if the payload is invalid (i.e. SEPARATOR is contained in payload),
    otherwise the packaged data in the following format:
    <length of data including separators>⣜⮾⼴<action>⣜⮾⼴<payload str (with delimiter SEPARATOR)>
    """
    if len(list(filter(lambda parameter: SEPARATOR in parameter, payload))):
        return None
    payload = f"{SEPARATOR}{action}{SEPARATOR}{SEPARATOR.join(payload)}"
    payload_len = len(payload)
    final_payload = f"{payload_len + len(str(payload_len))}{payload}"
    if (socket):
        socket.sendall(final_payload.encode('utf-8'))
    return final_payload


def unpackage(message):
    """
    Unpackages the message sent between the server and the client.
    @Parameter:
    1. message: The message to be unpackaged.
    @Returns: The unpackaged message in an array D where D[0] = count, D[1] = action, D[2] = content.
    """
    return message.split(SEPARATOR)


def receive_message(socket):
    """
    Blocks and waits to receive an entire message from a socket.
    @Parameter:
    1. socket: The socket to receive data from.
    @Returns: The message received from the socket othewise None if the socket is closed or the message is malformed.
    """
    count = None
    data = ""
    message = socket.recv(MAX_SOCKET_BUFFER_SIZE).decode('utf-8')
    if (not message):
        return None
    if SEPARATOR in message:
        try:
            count = int(message.split(SEPARATOR)[0])
        except ValueError:
            count = None
    if (count):
        count -= len(message)
        data += message
        while count > 0:
            newMsg = socket.recv(
                MAX_SOCKET_BUFFER_SIZE if MAX_SOCKET_BUFFER_SIZE > count else count
            ).decode('utf-8')
            count -= len(newMsg)
            data += newMsg
        return data
    else:
        return None


def receive_unpkg_data(socket):
    """
    Blocks and waits to receive an entire message from a socket and unpackages it.
    @Parameter:
    1. socket: The socket to receive data from.
    @Returns: The unpackaged message received from the socket otherwise None if the socket is closed or the message is malformed.
    """
    msg = receive_message(socket)
    if (not msg):
        return None
    return unpackage(msg)
