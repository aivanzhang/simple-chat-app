from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class PendingMsgsResponse(_message.Message):
    __slots__ = ["isEmpty", "message"]
    ISEMPTY_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    isEmpty: bool
    message: str
    def __init__(self, message: _Optional[str] = ..., isEmpty: bool = ...) -> None: ...

class UserReply(_message.Message):
    __slots__ = ["message"]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    message: str
    def __init__(self, message: _Optional[str] = ...) -> None: ...

class UserRequest(_message.Message):
    __slots__ = ["action", "message", "recipient", "username"]
    ACTION_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    RECIPIENT_FIELD_NUMBER: _ClassVar[int]
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    action: str
    message: str
    recipient: str
    username: str
    def __init__(self, action: _Optional[str] = ..., username: _Optional[str] = ..., recipient: _Optional[str] = ..., message: _Optional[str] = ...) -> None: ...
