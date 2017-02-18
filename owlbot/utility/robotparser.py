from urllib import robotparser


class RobotFileParser(robotparser.RobotFileParser):
    def __init__(self, code, content):
        super().__init__()
        self.code = code
        self.content = content
        self.read()

    def read(self):
        if self.code in (401, 403):
            self.disallow_all = True
        elif self.code >= 400 and self.code < 500:
            self.allow_all = True
        else:
            self.parse(self.content.decode("utf-8").splitlines())
