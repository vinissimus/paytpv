# encoding: utf-8


class PaytpvException(Exception):

    def __init__(self, code):
        super().__init__("Error: {}".format(code))
        self.code = int(code)
