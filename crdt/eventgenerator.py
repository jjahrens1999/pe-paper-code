import random
from random import randrange

from crdt.updateevent import UpdateEvent


class UpdateEventGenerator:
    def __init__(self, crdt_size, replication_id):
        self._crdt_size = crdt_size
        self._replication_id = replication_id

    def new_update(self) -> UpdateEvent:
        if random.random() >= 0.5:
            event_type = "increment"
        else:
            event_type = "decrement"

        event_path = randrange(self._crdt_size)

        return UpdateEvent(event_type, self._replication_id, event_path)