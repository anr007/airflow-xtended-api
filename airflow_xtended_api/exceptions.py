class Error(Exception):
    """Base class for exceptions in this module."""


class DagAlreadyExistsError(Error):
    def __init__(self, message, trace=None):
        super().__init__()
        self.message = message
        self.trace = trace


class DagDoesNotExistsError(Error):
    def __init__(self, message, trace=None):
        super().__init__()
        self.message = message
        self.trace = trace


class OSFileHandlingError(Error):
    def __init__(self, message, trace=None):
        super().__init__()
        self.message = message
        self.trace = trace


class S3GenericError(Error):
    def __init__(self, message, trace=None):
        super().__init__()
        self.message = message
        self.trace = trace


class S3BucketDoesNotExistsError(Error):
    def __init__(self, message, trace=None):
        super().__init__()
        self.message = message
        self.trace = trace


class S3ObjDownloadError(Error):
    def __init__(self, message, trace=None):
        super().__init__()
        self.message = message
        self.trace = trace


class MongoClientError(Error):
    def __init__(self, message, trace=None):
        super().__init__()
        self.message = message
        self.trace = trace


class NetworkRequestFailedError(Error):
    def __init__(self, message, trace=None):
        super().__init__()
        self.message = message
        self.trace = trace
