

class CmCrdtPNCounter:
    def __init__(self, value: int):
        self._counter = value

    def increment(self):
        self._counter += 1

    def decrement(self):
        self._counter -= 1

    def value(self):
        return self._counter