from aiocoap import *

class CoAPConSender:

    def __init__(self):
        self._context = None

    async def send(self, payload: bytes, target):
        if self._context is None:
            self._context = await Context.create_client_context()

        success = False

        while not success:
            request = Message(mtype = 0, code=3, payload=payload, uri=f"coap://{target}/publishUpdate")

            try:
                response = await self._context.request(request).response
                if response.code.is_successful():
                    success = True
            except:
                print("an error has occured while transmitting")