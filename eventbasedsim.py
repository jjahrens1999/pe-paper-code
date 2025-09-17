import argparse
import asyncio
import json
from typing import List

from coap.coapConSender import CoAPConSender
from coap.coapNonSender import CoAPNonSender
from coap.coapResource import CoAPResource
from crdt.eventgenerator import UpdateEventGenerator
from crdt.largecrdt import CombinedCrdt
import aiocoap.resource as resource
import aiocoap

from crdt.updateevent import UpdateEvent


async def event_based_simulation(sync_mode: str, replication_addrs: List[str], replication_id):
    crdt = CombinedCrdt(len(replication_addrs) + 1)

    event_generator = UpdateEventGenerator(crdt.crdt_size(), replication_id)

    update_backlog = []

    root = resource.Site()
    root.add_resource(["publishUpdate"], CoAPResource(update_backlog))

    await aiocoap.Context.create_server_context(root)

    # wait for other replications to start
    await asyncio.sleep(3)

    coap_sender = None
    if sync_mode == "con":
        coap_sender = CoAPConSender()
    elif sync_mode == "non":
        coap_sender = CoAPNonSender()

    # main update loop
    for i in range(20):
        print(f"loop step {i}")
        for _ in range(30):
            update = event_generator.new_update()
            crdt.apply_update(update)
            update_json = json.dumps(update.to_json())
            for replication in replication_addrs:
                await coap_sender.send(update_json.encode("utf-8"), replication)
        await asyncio.sleep(1)
        while len(update_backlog) > 0:
            remote_update = update_backlog.pop()
            print(remote_update)
            crdt.apply_update(UpdateEvent.from_json(remote_update))
        print(json.dumps(crdt.to_json(), indent=4))

    await asyncio.sleep(2)
    # be sure to catch every update
    for remote_update in update_backlog:
        crdt.apply_update(UpdateEvent.from_json(remote_update))
    print(json.dumps(crdt.to_json(), indent=4))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("replication_id")
    parser.add_argument("replication_addr")
    args = parser.parse_args()
    asyncio.run(event_based_simulation("non", [args.replication_addr], int(args.replication_id)))