class AsyncAnthropic:
    def __init__(self, *args, **kwargs):
        pass


class AnthropicError(Exception):
    pass


class APIConnectionError(AnthropicError):
    pass


class APITimeoutError(AnthropicError):
    def __init__(self, request=None, *args, **kwargs):
        super().__init__(*args)
        self.request = request


class AuthenticationError(AnthropicError):
    def __init__(self, message=None, response=None, body=None):
        super().__init__(message)
        self.response = response
        self.body = body


class RateLimitError(AnthropicError):
    def __init__(self, message=None, response=None, body=None):
        super().__init__(message)
        self.response = response
        self.body = body


class APIStatusError(AnthropicError):
    pass
