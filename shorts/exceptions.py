

class AppException(Exception):
    def __init__(self, message='Unexpected error', status_code=500):
        self.message = message
        self.status_code = status_code
