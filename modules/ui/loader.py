import threading
import time

from .line import delete_line
from .completer import Completer
from .item import UItem


class Loader(UItem):
    """
    an indefinite loader

    change message mid execution to change display hint

    use
    with Loader(msg) as l:

        # to show fail
        l.fail(*optional_msg)

    or use decorators for functions
    """

    FULL_BLOCK = '\u2588'
    EMPTY_SPACE = ' '

    # this has been left like this for sake of clear understanding
    STATES = [
        (EMPTY_SPACE * 0) + (FULL_BLOCK * 1) + (EMPTY_SPACE * 4),
        (EMPTY_SPACE * 0) + (FULL_BLOCK * 2) + (EMPTY_SPACE * 3),
        (EMPTY_SPACE * 0) + (FULL_BLOCK * 3) + (EMPTY_SPACE * 2),
        (EMPTY_SPACE * 0) + (FULL_BLOCK * 4) + (EMPTY_SPACE * 1),
        (EMPTY_SPACE * 0) + (FULL_BLOCK * 5) + (EMPTY_SPACE * 0),
        (EMPTY_SPACE * 1) + (FULL_BLOCK * 4) + (EMPTY_SPACE * 0),
        (EMPTY_SPACE * 2) + (FULL_BLOCK * 3) + (EMPTY_SPACE * 0),
        (EMPTY_SPACE * 3) + (FULL_BLOCK * 2) + (EMPTY_SPACE * 0),
        (EMPTY_SPACE * 4) + (FULL_BLOCK * 1) + (EMPTY_SPACE * 0),
        (EMPTY_SPACE * 5) + (FULL_BLOCK * 0) + (EMPTY_SPACE * 0),
    ]

    def __init__(self, s):
        super().__init__(s)

        self.thread = DrawingThread(message=s)
        self.thread.daemon = True

    @property
    def message(self):
        return self._message

    @message.setter
    def message(self, val):
        self.thread.set_message(val)
        self._message = val

    def set_drawing_speed(self, speed):
        self.thread.drawing_speed = speed

    def init(self):
        # start drawing
        self.thread.start()

        return self

    def complete(self):
        super().complete()

        # stop drawing
        self.thread.stop(error=False)

        # sanity check
        while self.thread.is_alive():
            pass

    def fail(self):
        super().fail()

        # stop drawing
        self.thread.stop(error=True)

        # sanity check
        while self.thread.is_alive():
            pass


class DrawingThread(threading.Thread):
    """Thread class that draws indefinitely until stoppped"""

    def __init__(self, message='', *args, **kwargs):
        super(DrawingThread, self).__init__(*args, **kwargs)
        self.message = message
        self.message_changed = False

        self.error = False
        self.drawing_speed = 0.1
        self._stop_event = threading.Event()

    def stop(self, error=False):
        self._stop_event.set()
        self.error = error

    def stopped(self) -> bool:
        return self._stop_event.is_set()

    def set_message(self, message):
        self.message_changed = True
        self.message = message

    def run(self) -> None:
        index = 0
        while True:
            if self.message_changed:
                delete_line()
                self.message_changed = False

            print(f'\r[{Loader.STATES[index]}] {self.message}', end='')

            if self.stopped():
                delete_line()
                c = Completer(f'{self.message}').init()
                if not self.error:
                    c.complete()
                else:
                    c.fail()
                return

            time.sleep(0.1)
            index = (index + 1) % len(Loader.STATES)
