# simple-chat-app

## Instructions for deploying

TODO: directions for deploying the server on cloud and connecting clients to the server.

### Server
Non-gRPC version: `python server/main.py`

gRPC version: `python server/main.py --use_grpc`

Mismatch in gRPC version between server and client will cause undefined behavior.

### Client
Non-gRPC version: `python client/main.py`

gRPC version: `python client/main.py --use_grpc`

Mismatch in gRPC version between server and client will cause undefined behavior.

#### Client Usage
The UI will ask for your username. You will not be able to log into a username if that username is already logged in elsewhere.

After entering your username, pending messages will be displayed.

Into the prompt `> ` you can perform the following actions:
- `list` will list all users.
- `send <user>` will initiate a send to a recipient user. Enter the message to be sent in the following prompt `>>>`.
- `delete <user>` will delete a user. You cannot delete yourself and you cannot delete a user who is logged in elsewhere.
- `quit` will quit the client, shutting down the connection.