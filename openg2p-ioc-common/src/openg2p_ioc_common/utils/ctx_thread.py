import contextvars
from threading import Thread


class CTXThread(Thread):
    def __init__(self, *args, **kwargs):
        self.ctx = contextvars.copy_context()
        super().__init__(*args, **kwargs)

    def run(self):
        self.ctx.run(super().run)
