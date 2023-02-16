# Tests

The following tests below run the application through the full gamut of UI behaviors. Use them to check for code correctness. These tests apply to both the wire protocol part 1 version and the gRPC part 2 version.

Setup: Start up the server and client as described in the README.

## Single User

For these tests, run a single client.

Login using a new username. You should not receive any pending messages.

Run `list` and ensure that your new username is included in the list.

Send a message to yourself with `send <your username>`. Enter a message. The message should be rerouted back to you in the form `<username> says: <message>`

Send a message to a non-user. You should receive an error message.

Attempt to delete your own username with `delete <your username>`. You should not be able to.

Attempt to quit with `quit`. There should be no issues.

You are now logged out. Run the client again and login with the same username. Quit again.

Now, login with a different unique username. Delete your first username and use `list` to ensure that it has been deleted.

Attempt to send a message to the deleted username. You should receive an error message.

Attempt to use a bogus user command. It should be unrecognized.

Attempt to quit using a keyboard interrupt. Log back in and ensure behavior is as expected. Quit.

## Two Users

For these tests, you will use two clients **A** and **B**. Use unique usernames which have not been used before.

Login to A. Attempt to send messages to B, since you haven't yet created B you should receive error messages.

While A is currently logged in, attempt to login to A from a different console. You should not be able to login to A since there is an active connection.

Login to B. You should not receive the messages that A had sent yet.

From A, send messages to B. Ensure that the message is received at B without much delay.

From B, send messages to A. Ensure that the message is received at A without much delay.

Logout of B. From A, send messages to B. Log back into B and ensure that the messages are delivered on login.

Repeat the above step logging out of A and sending from B.

With both A and B logged in, attempt to delete A from B and B from A. You should not be able to delete the accounts as they are logged in. Use `list` to ensure the accounts have not been deleted.

Quit from A using a keyboard interrupt. B `list` should still show A exists. Send messages from B to A and log back into A. Ensure that the pending messages are received.

## Three Users

For these tests, use three clients **A**, **B**, and **C**.

From A, send messages to B and ensure that nothing happens to C. Do this while B is logged in and while B is logged out.

From A and C, both send messages to B. Do this while B is logged in and while B is logged out.

Logout of A. From B, delete A. Check from both B and C that `list` shows A as deleted.