class AsyncGroq:
    def __init__(self, *args, **kwargs):
        pass


class GroqError(Exception):
    pass


class APIConnectionError(GroqError):
    pass


class APITimeoutError(GroqError):
    def __init__(self, request=None, *args, **kwargs):
        super().__init__(*args)
        self.request = request


class AuthenticationError(GroqError):
    def __init__(self, message=None, response=None, body=None):
        super().__init__(message)
        self.response = response
        self.body = body


class RateLimitError(GroqError):
    def __init__(self, message=None, response=None, body=None):
        super().__init__(message)
        self.response = response
        self.body = body


class BadRequestError(GroqError):
    pass
