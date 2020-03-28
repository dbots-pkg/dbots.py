class DBotsException(Exception):
    """Base exception class for dbots

    This can be used to handle any exception from dbots.
    """
    pass

class PosterException(DBotsException):
    """Exception that is thrown when the poster encounters an error."""
    pass

class ClientException(PosterException):
    """Exception that is thrown when the options for a client is invalid."""
    pass

class ServiceException(PosterException):
    """Exception that is thrown when the options for a service is invalid."""
    pass

class APIKeyException(PosterException):
    """Exception that is thrown when an API key is invalid."""
    pass

class HTTPException(DBotsException):
    """Exception that is thrown when an HTTP request has an error."""
    def __init__(self, response):
        self.response = response
        self.status = response.status
        self.body = response.body

        fmt = '{0.raw.method} {0.status}, {0.raw.url}'
        if len(self.body):
            fmt = fmt + ': {1}'

        super().__init__(fmt.format(self.response, self.body))

class HTTPForbidden(HTTPException):
    """Exception that's thrown for when status code 403 occurs.
    Subclass of :exc:`HTTPException`
    """
    pass

class HTTPUnauthorized(HTTPException):
    """Exception that's thrown for when status code 403 occurs.
    Subclass of :exc:`HTTPException`
    """
    pass

class HTTPNotFound(HTTPException):
    """Exception that's thrown for when status code 404 occurs.
    Subclass of :exc:`HTTPException`
    """
    pass

class EndpointRequiresToken(DBotsException):
    """Exception that's thrown for when an endpoint is being used without a token."""
    def __init__(self):
        super().__init__('This endpoint requires a token.')

class PostingUnsupported(ServiceException):
    """Exception that's thrown for services that cannot be posted to."""
    def __init__(self):
        super().__init__('This service does not support posting.')