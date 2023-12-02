

class InvalidCommStateError(Exception):

    def __init__(self, message: str = "Communication state invalid!") -> None:
        super().__init__(message)

class IllegalServerState(Exception):
    def __init__(self, message: str = "Server state invalid!") -> None:
        super().__init__(message)