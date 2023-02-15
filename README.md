# simple-chat-app

## Instructions for deploying

These instructions are AWS-specific but similar requirements will apply to other cloud providers.

1. Spin up an EC2 instance.
2. Ensure that the vpc has an internet gateway attached to it so that it can be publicly accessed.
3. Ensure that the security group allows inbound traffic on port 3000 (for server) and 22 (for ssh access).
4. Download the simple-chat-app repository to the EC2 instance.
5. Install the required dependencies by running `pip install -r requirements.txt`.
6. Run the server by running `cd server; python main.py --use_aws [--use_grpc]`.
7. Edit the client/main.py file to change the `aws_host` variable to the public IP of the EC2 instance.
8. Run the client by running `cd client; python main.py --use_aws [--use_grpc]`.

### Generating grpc stubs (Not Required)

If you want to generate the grpc stubs yourself, you can do so by running the following commands:
`./generate_grpc_stubs.sh`

### Server

Non-gRPC version: `cd server; python main.py`

gRPC version: `cd server; python main.py --use_grpc`

Mismatch in gRPC version between server and client will cause undefined behavior.

### Client

Non-gRPC version: `cd client; python main.py`

gRPC version: `cd client; python main.py --use_grpc`

Mismatch in gRPC version between server and client will cause undefined behavior.

#### Client Usage

The UI will ask for your username. You will not be able to log into a username if that username is already logged in elsewhere.

After entering your username, pending messages will be displayed.

Into the prompt `> ` you can perform the following actions:

- `list` will list all users.
- `send <user>` will initiate a send to a recipient user. Enter the message to be sent in the following prompt `>>>`.
- `delete <user>` will delete a user. You cannot delete yourself and you cannot delete a user who is logged in elsewhere.
- `quit` will quit the client, shutting down the connection.
