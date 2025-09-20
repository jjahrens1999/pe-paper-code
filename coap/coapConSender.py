from aiocoap import *

class CoAPConSender:

    def __init__(self, context):
        self._context = context

    async def send(self, payload: bytes, target):
        request = Message(mtype=0, code=3, payload=payload, uri=f"coap://{target}/publishUpdate")

        await self._context.request(request).response
