class ResponseError(Exception):

    def __init__(self, status_code, type, message):
        self.status_code = status_code
        self.type = type
        self.message = message
        super().__init__(self.message)