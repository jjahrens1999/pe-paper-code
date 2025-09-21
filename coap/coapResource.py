# Based on https://aiocoap.readthedocs.io/en/latest/examples.html

import json
from typing import List, Any

import aiocoap.resource as resource
from aiocoap import *

class CoAPResource(resource.Resource):
    def __init__(self, update_backlog: List[Any]):
        super().__init__()
        self._update_backlog = update_backlog

    async def render_put(self, request):
        self._update_backlog.append(json.loads(request.payload.decode("utf-8")))
        if request.mtype == 0:
            return Message(mtype=2, code=68)
        return NoResponse
