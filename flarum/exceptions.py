
# Meta Exceptions
class FlarumBadUrl(Exception):
    """Raised if we can't see a flarum API at the URL provided"""
class FlarumAuthException(Exception):
    """Raised when any error occurs relating to lack of permissions"""


class FlarumAPIException(Exception):
    """Base Exception for all flarum exceptions"""
    def __init__(self, r):
        message = "Call to %s %s failed with HTTP code %s" % (r.request.method, r.url, r.status_code)
        super(FlarumAPIException, self).__init__(message)


# 4xx Client Errors
class Flarum4XXClientError(FlarumAPIException):
    """Raised on any 4xx exception"""
class FlarumBadRequest(Flarum4XXClientError):
    """400"""
class FlarumUnauthorised(Flarum4XXClientError):
    """401"""
class FlarumForbidden(Flarum4XXClientError):
    """403"""
class FlarumNotFound(Flarum4XXClientError):
    """404"""
class FlarumMethodNotAllowed(Flarum4XXClientError):
    """405"""
class FlarumConflict(Flarum4XXClientError):
    """409"""

# 5xx Server Errors
class Flarum5XXServerError(FlarumAPIException):
    """Raised on any 5xx exception"""
class FlarumInternalServerError(Flarum5XXServerError):
    """500"""
class FlarumNotImplemented(Flarum5XXServerError):
    """501"""
class FlarumBadGateway(Flarum5XXServerError):
    """502"""
class FlarumGatewayTimeout(Flarum5XXServerError):
    """504"""


EXCEPTION_MAP = {
    400: Flarum4XXClientError,
    401: FlarumBadRequest,
    403: FlarumForbidden,
    404: FlarumNotFound,
    405: FlarumMethodNotAllowed,
    409: FlarumConflict,

    500: FlarumInternalServerError,
    501: FlarumNotImplemented,
    502: FlarumBadGateway,
    504: FlarumGatewayTimeout
}

def error_code_handler(r):
    """Raises an exception if necessary based on the requests status code"""
    if r.status_code in EXCEPTION_MAP:
        raise EXCEPTION_MAP[r.status_code](r)

    if 400 <= r.status_code <= 499:
        raise Flarum4XXClientError(r)
    if 500 <= r.status_code <= 599:
        raise Flarum5XXServerError(r)