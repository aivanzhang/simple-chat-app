from enum import Enum
import pickle


class Actions(Enum):
    """
    Actions that can be performed by the client and server.
    """
    CREATE = 0,
    LIST = 1,
    SEND = 2,
    DELETE = 3,


class Mode(Enum):
    """
    Mode that the encode and decode function should run in.
    """
    CLIENT = 0,
    SERVER = 1,


class CreatePayload():
    TYPE = Actions.CREATE
    QUESTION = "What is your username? ".encode('utf-8')
    username = None

    def __init__(self, username=None):
        self.username = username

    def getUsername(self):
        return self.username


def encode(action: Actions, mode: Mode, payload={}):
    payload = None
    if (mode == Mode.CLIENT):
        if (action == Actions.CREATE):
            payload = CreatePayload(payload.username.encode('utf-8'))

    if (mode == Mode.SERVER):
        if (action == Actions.CREATE):
            payload = CreatePayload()

    return pickle.dumps(payload)


def decode(data):
    return pickle.loads(data)
