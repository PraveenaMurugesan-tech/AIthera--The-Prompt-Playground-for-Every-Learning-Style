class GoogleAPICallError(Exception):
    pass


class Unauthenticated(GoogleAPICallError):
    pass


class PermissionDenied(GoogleAPICallError):
    pass


class DeadlineExceeded(GoogleAPICallError):
    pass


class ServiceUnavailable(GoogleAPICallError):
    pass


class ResourceExhausted(GoogleAPICallError):
    pass


class InvalidArgument(GoogleAPICallError):
    pass
