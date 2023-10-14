import logging

from fastapi.exceptions import RequestValidationError, ResponseValidationError
from fastapi.responses import ORJSONResponse

from .component import BaseComponent
from .context import app_registry
from .errors import BaseAppException, ErrorListResponse, ErrorResponse

_logger = logging.getLogger(__name__)


class BaseExceptionHandler(BaseComponent):
    def __init__(self, name="", **kwargs):
        super().__init__(name=name)

        app = app_registry.get()
        app.add_exception_handler(BaseAppException, self.base_exception_handler)
        app.add_exception_handler(
            RequestValidationError, self.request_validation_exception_handler
        )
        app.add_exception_handler(
            ResponseValidationError, self.response_validation_exception_handler
        )
        app.add_exception_handler(Exception, self.unknown_exception_handler)

    async def base_exception_handler(self, request, exc: BaseAppException):
        _logger.exception(f"Received Exception: {exc}")
        # TODO: Handle multiple exceptions
        res = ErrorListResponse(
            errors=[ErrorResponse(code=exc.code, message=exc.message)]
        )
        return ORJSONResponse(
            content=res.model_dump(), status_code=exc.http_status_code
        )

    async def request_validation_exception_handler(
        self, request, exc: RequestValidationError
    ):
        _logger.error(
            "Received exception: %s",
            repr(exc),
            extra={"props": {"exc_info": exc.errors()}},
        )
        # _logger.exception("Received exception: %s", repr(exc))
        errors = []
        for err in exc.errors():
            err_msg = err.get("msg")
            errors.append(
                ErrorResponse(code="G2P-REQ-102", message=f"Invalid Input. {err_msg}")
            )
        res = ErrorListResponse(errors=errors)
        return ORJSONResponse(content=res.model_dump(), status_code=400)

    async def response_validation_exception_handler(
        self, request, exc: ResponseValidationError
    ):
        _logger.exception("Received exception: %s", repr(exc))
        errors = []
        for err in exc.errors():
            errors.append(
                ErrorResponse(
                    code="G2P-RES-100",
                    message=f"Internal Server Error. Invalid Response. {err}",
                )
            )
        res = ErrorListResponse(errors=errors)
        return ORJSONResponse(content=res.model_dump(), status_code=500)

    async def unknown_exception_handler(self, request, exc):
        _logger.exception("Received Unknown Exception: %s", repr(exc))
        exc_split = str(exc).split("::")
        if len(exc_split) > 1:
            code = exc_split[0]
            message = exc_split[1]
        else:
            code = "G2P-REQ-100"
            message = exc_split[0]
        res = ErrorListResponse(errors=[ErrorResponse(code=code, message=message)])
        return ORJSONResponse(content=res.model_dump(), status_code=500)
