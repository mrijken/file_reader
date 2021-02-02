class Auth:
    pass


class UsernamePassword(Auth):
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
