class Request:
    def __init__(self, method: str, url: str):
        self.method = method
        self.url = url


class Response:
    def __init__(self, status_code: int, request: Request = None):
        self.status_code = status_code
        self.request = request

    def json(self):
        return {}
