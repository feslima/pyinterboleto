class PyInterBoletoException(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__()


class AuthenticationFailedException(PyInterBoletoException):
    pass
