class FilevineException(Exception):
    def __init__(self, msg=None, url=None):
        if not msg:
            msg = "An error occurred when trying to access the filevine API"
            if url is not None:
                msg += f" at {url}"
        super(FilevineException, self).__init__(msg)
        self.url = url
        self.msg = msg


class FilevineHTTPException(FilevineException):
    def __init__(self, code, url=None, msg=None):
        self.code = code
        if not msg:
            msg = f"Received non-2xx HTTP Status Code {code}"
        super(FilevineHTTPException, self).__init__(msg=msg, url=url,)


class FilevineTypeError(FilevineException, TypeError):
    def __init__(self, expected_type, received_type):
        msg = f"Type {expected_type} required in API definition, but received {received_type}"
        super(FilevineTypeError, self).__init__(msg=msg)


class FilevineValueError(FilevineException, ValueError):
    def __init__(self, msg=None):
        if not msg:
            msg = "Given parameter does not meet argument requirements"
        super(FilevineValueError, self).__init__(msg=msg)
