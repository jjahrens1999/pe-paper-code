# Based on https://www.cs.utexas.edu/~rossbach/cs380p/papers/Counters.html

from typing import List, Any, Dict

from crdt.updateevent import UpdateEvent


class PNCounter:
    def __init__(self,
                 nreplicas: int,
                 increments: List[int] = None,
                 decrements: List[int] = None):
        self._nreplicas = nreplicas
        if increments is None:
            self._increments = [0] * nreplicas
        else:
            self._increments = increments
        if decrements is None:
            self._decrements = [0] * nreplicas
        else:
            self._decrements = decrements

    def increments(self) -> List[int]:
        # return a copy of the increments
        return self._increments

    def decrements(self) -> List[int]:
        # return a copy of the decrements
        return self._decrements

    def value(self):
        return (sum(self.increments()) -
                sum(self.decrements()))

    def increment(self, replica_id: int):
        self._increments[replica_id] += 1

    def decrement(self, replica_id: int):
        self._decrements[replica_id] += 1

    def compute_sum(self) -> int:
        return (sum(self.increments()) +
                sum(self.decrements()))

    def compute_delta(self, other) -> int:
        return sum(
            [abs(self.increments()[i] - other.increments()[i]) + abs(self.decrements()[i] - other.decrements()[i]) for i
             in range(self._nreplicas)])

    def compute_delta_percentage(self, other) -> float:
        return self.compute_delta(other) / max(self.compute_sum(), other.compute_sum())

    def merge(self, other):
        self._increments=[max(self.increments()[i], other.increments()[i]) for i in range(self._nreplicas)]
        self._decrements=[max(self.decrements()[i], other.decrements()[i]) for i in range(self._nreplicas)]

    def apply_update(self, event: UpdateEvent):
        if event.type() == "increment":
            self.increment(event.node())
        elif event.type() == "decrement":
            self.decrement(event.node())

    @classmethod
    def from_json(cls, json_obj: Any, nreplicas: int):
        return PNCounter(nreplicas, json_obj["increments"], json_obj["decrements"])

    def to_json(self) -> Dict:
        return {"increments": self.increments(), "decrements": self.decrements()}

    def crdt_size(self) -> int:
        return 0
