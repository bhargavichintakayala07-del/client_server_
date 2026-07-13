USERS = {
    "student1": "1234",
    "student2": "5678"
}


def authenticate(username, password):

    if username in USERS:

        if USERS[username] == password:
            return True

    return False