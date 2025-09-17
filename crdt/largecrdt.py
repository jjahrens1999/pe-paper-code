from typing import List, Any, Dict

from crdt.pncounter import PNCounter
from crdt.updateevent import UpdateEvent

CRDT_SIZE = 30

class CombinedCrdt:
    def __init__(self, nreplicas: int, counters: List[PNCounter] = None):
        if counters is None:
            self._counters = [PNCounter(nreplicas) for _ in range(CRDT_SIZE)]
        else:
            self._counters = counters

    def increment(self, replica_id: int, path: int):
        self._counters[path].increment(replica_id)

    def decrement(self, replica_id: int, path: int):
        self._counters[path].decrement(replica_id)

    def counters(self) -> List[PNCounter]:
        return self._counters

    def compute_sum(self) -> int:
        return sum([counter.compute_sum() for counter in self.counters()])

    def compute_delta(self, other) -> int:
        return sum([own_counter.compute_delta(other_counter) for (own_counter, other_counter) in zip(self.counters(), other.counters())])

    def computer_delta_percentage(self, other):
        return self.compute_delta(other) / max(self.compute_sum(), other.compute_sum())

    def merge(self, other):
        for (own_counter, other_counter) in zip(self.counters(), other.counters()):
            own_counter.merge(other_counter)

    def apply_update(self, event: UpdateEvent):
        if event.type() == "increment":
            self.increment(event.node(), event.path())
        elif event.type() == "decrement":
            self.decrement(event.node(), event.path())

    @classmethod
    def from_json(cls, json_obj: Any, nreplicas: int):
        return CombinedCrdt(nreplicas, [PNCounter.from_json(counter, nreplicas) for counter in json_obj["counters"]])

    def to_json(self) -> Dict:
        return {"counters": [counter.to_json() for counter in self._counters]}

    def crdt_size(self) -> int:
        return len(self._counters)
