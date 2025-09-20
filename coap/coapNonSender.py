from aiocoap import *

class CoAPNonSender:

    def __init__(self, context):
        self._context = context

    async def send(self, payload: bytes, target):
        request = Message(mtype = 1, code=3, payload=payload, uri=f"coap://{target}/publishUpdate")

        self._context.request(request)
