from .base_exception import BaseAppException


class UnauthorizedError(BaseAppException):
    def __init__(
        self, code="G2P-AUT-401", message="Unauthorized", http_status_code=401, **kwargs
    ):
        super().__init__(code, message, http_status_code, **kwargs)


class ForbiddenError(BaseAppException):
    def __init__(
        self, code="G2P-AUT-403", message="Forbidden", http_status_code=403, **kwargs
    ):
        super().__init__(code, message, http_status_code, **kwargs)


class BadRequestError(BaseAppException):
    def __init__(
        self,
        code="G2P-REQ-400",
        message="Generic Bad Request",
        http_status_code=400,
        **kwargs
    ):
        super().__init__(code, message, http_status_code, **kwargs)
