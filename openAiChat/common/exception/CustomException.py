class CustomException(Exception):
    def __init__(self, error_code, message):
        self.error_code = error_code
        self.message = message
        super().__init__(f"错误码: {self.error_code}, 错误信息: {self.message}")