class ApplicationError(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        super(ApplicationError, self).__init__()
        self.message = message
        self.status_code = status_code or self.status_code
        self.payload = payload

    def to_dict(self):
        ret = self.payload or {}
        ret['status'] = self.status_code
        ret['message'] = self.message
        return ret


class ResponseException(Exception):
    def __init__(self, message, status=500, error_class=None, error_type=None, **kwargs):
        super(ResponseException, self).__init__(message)
        self.status = status  # This will be used for the HTTP response status code, 500 if unspecified
        self.errorType = error_type  # This is used for writing to the error DB
        self.extraInfo = {}
        for key in kwargs:
            # Include extra error info
            self.extraInfo[key] = kwargs[key]  # This can be written to the error DB for some error types
        if error_class is None:
            self.wrappedException = None  # Can be used to wrap another type of exception into a ResponseException
        else:
            try:
                self.wrappedException = error_class(message)
            except Exception:
                # Some errors cannot be created with just a message, in that case create a string representation
                self.wrappedException = str(error_class) + str(message)
