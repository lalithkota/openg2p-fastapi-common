class BaseException(Exception):
    def __init__(self, code, message, **kwargs):
        super().__init__(message)
        self.code = code
