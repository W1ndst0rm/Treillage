class TreillageException(Exception):
    def __init__(self, msg=None, url=None):
        if not msg:
            msg = "An error occurred when trying to access the Filevine API"
            if url is not None:
                msg += f" at {url}"
        super(TreillageException, self).__init__(msg)
        self.url = url
        self.msg = msg


class TreillageHTTPException(TreillageException):
    def __init__(self, code, url=None, msg=None):
        self.code = code
        if not msg:
            msg = f"Received non-2xx HTTP Status Code {code}"
        super(TreillageHTTPException, self).__init__(msg=msg, url=url, )


class TreillageRateLimitException(TreillageHTTPException):
    def __init__(self, url=None, msg=None):
        self.code = 429
        if not msg:
            msg = "Server Rate Limit Exceeded"
        super(TreillageRateLimitException, self).__init__(self.code, url, msg)


class TreillageTypeError(TreillageException, TypeError):
    def __init__(self, expected_type, received_type):
        msg = (f"Type {expected_type} required in API definition, " +
               f"but received {received_type}")
        super(TreillageTypeError, self).__init__(msg=msg)


class TreillageValueError(TreillageException, ValueError):
    def __init__(self, msg=None):
        if not msg:
            msg = "Given parameter does not meet argument requirements"
        super(TreillageValueError, self).__init__(msg=msg)
