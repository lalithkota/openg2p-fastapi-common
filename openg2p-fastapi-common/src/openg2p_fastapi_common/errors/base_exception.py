class BaseAppException(Exception):
    def __init__(self, code, message, http_status_code=500, **kwargs):
        # TODO: Handle Multiple Exceptions
        super().__init__(message)
        self.code = code
        self.message = message
        self.http_status_code = http_status_code

    def __str__(self):
        return f'{type(self).__name__}("{self.code}", "{self.message}")'

    def __repr__(self):
        return f'{type(self).__name__}("{self.code}", "{self.message}")'
