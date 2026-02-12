class BaseAppException(Exception):
    def __init__(self, *kw):
        super().__init__(*kw)
        self.code = None
        self.message = None
