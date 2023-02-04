from enum import Enum


class Action(str, Enum):
    """
    Actions that can be performed by the client and server.
    """
    CREATE = "create",
    LIST = "list",
    SEND = "send",
    DELETE = "delete",


SEPARATOR = "⣜⮾⼴"

COUNT_IDENTIFIER = "ⓘ…Ⲉ"


def encode(action: Action, content=""):
    """
    Encodes the data to be sent between the server and the client.
    @Parameter:
    1. action: The action to be performed.
    2. content: The content to be sent.
    @Returns: The encoded data in the following format:
    ⓘ…Ⲉ<length of data including separators>⣜⮾⼴<action>⣜⮾⼴<content>
    """
    payload = f"{SEPARATOR}{action}{SEPARATOR}{content}"
    payload_len = len(payload) + len(COUNT_IDENTIFIER)
    return f"{COUNT_IDENTIFIER}{payload_len + len(str(payload_len))}{payload}"


def decode(data):
    """
    Decodes the data sent between the server and the client.
    @Parameter:
    1. data: The data to be decoded.
    @Returns: The decoded data in an array D where D[0] = count, D[1] = action, D[2] = content.
    """
    return data.split(SEPARATOR)


print(encode(Action.CREATE, "Hello World"))
