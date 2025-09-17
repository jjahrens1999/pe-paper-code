from aiocoap import *

class CoAPNonSender:

    def __init__(self):
        self._context = None

    async def send(self, payload: bytes, target):
        if self._context is None:
            self._context = await Context.create_client_context()

        request = Message(mtype = 1, code=3, payload=payload, uri=f"coap://{target}/publishUpdate")
        self._context.request(request)
