"""
`users` is a global dictionary that stores the user data. The key is the username of the user
and the value is an array of the user's pending messages as strings. So for example,
if the user "bob" has pending messages "hello" and "goodbye", then `users` will be:
{
    "bob": ["hello", "goodbye"]
}
"""
users = dict()


def init_db(database_name: str = "users") -> None:
    """
    Creates database file `database_name`.csv if it exists, otherwise finish.
    @Parameter:
    1. database_name: str = file name for the database.
    @Returns: None.
    """
    with open("{}.csv".format(database_name), "w+"):
        return


def init_users() -> None:
    """
    Initializes the `users` dictionary by reading the database file `users.csv`.
    @Parameter: None.
    @Returns: None.
    @Raises: FileNotFoundError if `users.csv` does not exist.
    """
    with open("users.csv", "r") as f:
        for line in f:
            line = line.strip().split(",")
            users[line[0]] = line[1:]
    return


def user_exists(username: str):
    """
    Returns True if the user exists in the database, False otherwise.
    @Parameter:
    1. username: str = username of the user to be checked.
    @Returns: True if the user exists in the database, False otherwise.
    """
    return username in users


def create_user(username: str) -> bool:
    """
    Returns True if the user was created successfully, False otherwise.
    @Parameter:
    1. username: str = username of the user to be created.
    @Returns: True if the user was created successfully, False otherwise.
    """
    if (not user_exists(username)):
        return False
    users[username] = []
    return True


def list_users() -> 'list[str]':
    """
    Returns a list of all the users in the database.
    @Parameter: None.
    @Returns: list of all the users in the database.
    """
    return list(users.keys())


def get_pending_messages(username: str) -> 'list[str]':
    """
    Returns a list of all the pending messages for a specific user.
    @Parameter:
    1. username: str = username of the user whose messages you want.
    @Returns: list of all the pending messages of a user in the database. If the 
    user does not exist then return an empty array.
    """
    if (not user_exists(username)):
        return []
    return users[username]


def clear_pending_messages(username: str) -> None:
    """
    Clears the pending messages for a user.
    @Parameter:
    1. username: str = username of the user.
    @Returns: None.
    """
    if (user_exists(username)):
        users[username] = []


def return_pending_messages(username: str) -> 'list[str]':
    """
    Returns all the pending messages for a user. Then clears the pending messages for that user.
    @Parameter:
    1. username: str = username of the user.
    @Returns: list of all the pending messages of a user in the database. If the 
    user does not exist then return an empty array.
    """
    if (user_exists(username)):
        messages = get_pending_messages(username)
        clear_pending_messages(username)
        return messages
    return []


def delete_user(username: str) -> None:
    """
    Deletes a user from the database. If the user has pending messages, they are deleted as well.
    @Parameter:
    1. username: str = username of the user.
    @Returns: None.
    """
    if (user_exists(username)):
        del users[username]
    return
