from typing import Dict


class UpdateEvent:
    def __init__(self, typ: str, node: int, path: int):
        self._type = typ
        self._node = node
        self._path = path

    def to_json(self) -> Dict:
        return {"node": self._node, "type": self._type, "path": self._path}

    @classmethod
    def from_json(cls, json_obj: Dict):
        return UpdateEvent(json_obj["type"], json_obj["node"], json_obj["path"])

    def node(self):
        return self._node

    def type(self):
        return self._type

    def path(self):
        return self._path