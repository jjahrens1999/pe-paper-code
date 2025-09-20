import argparse
import asyncio
import json
import os
import time
from typing import List, Any

from aiocoap import Context

from coap.coapConSender import CoAPConSender
from coap.coapNonSender import CoAPNonSender
from coap.coapResource import CoAPResource
from crdt.eventgenerator import UpdateEventGenerator
from crdt.compoundcrdt import CompoundCrdt
import aiocoap.resource as resource
import aiocoap

from crdt.updateevent import UpdateEvent

import logging

async def run_single_simulation(request_mode: str, sync_mode: str, replication_addrs: List[str], replication_id: str, name: str, nrepeat: int):
    log_dir_name = f"sim-results/{name}"
    logfile_name = f'{log_dir_name}/log-node{replication_id}.txt'
    json_dir_name = f"{log_dir_name}/repeat-{nrepeat}/node-{replication_id}"
    if not os.path.exists(log_dir_name):
        os.mkdir(log_dir_name)
    if not os.path.exists(logfile_name):
        open(logfile_name, "w")
    if not os.path.exists(json_dir_name):
        os.makedirs(json_dir_name)

    # Configure the logger
    logging.basicConfig(
        filename=logfile_name,  # Specify the log file name
        filemode="a",
        level=logging.INFO,  # Set the logging level to INFO
        format='%(asctime)s - %(levelname)s - %(message)s'  # Define the log message format
    )

    logging.info(f'Starting simulation with name {name} repeat {nrepeat} at timestamp {time.time()}')

    nreplicas = len(replication_addrs) + 1
    crdt = CompoundCrdt(nreplicas)

    event_generator = UpdateEventGenerator(crdt.crdt_size(), replication_id)

    update_backlog = []

    root = resource.Site()
    root.add_resource(["publishUpdate"], CoAPResource(update_backlog))

    server_context = await aiocoap.Context.create_server_context(root)
    context = await Context.create_client_context()

    # wait for other replications to start
    await asyncio.sleep(3)

    coap_sender = None
    if request_mode == "con":
        coap_sender = CoAPConSender(context)
    elif request_mode == "non":
        coap_sender = CoAPNonSender(context)

    # main update loop
    for i in range(20):
        print(f"loop step {i}")
        for _ in range(5):
            update = event_generator.new_update()
            crdt.apply_update(update)
            if sync_mode == "operation":
                update_json = json.dumps(update.to_json())
                for replication in replication_addrs:
                    asyncio.create_task(coap_sender.send(update_json.encode("utf-8"), replication))
        if sync_mode == "state":
            state_json = json.dumps(crdt.to_json())
            for replication in replication_addrs:
                asyncio.create_task(coap_sender.send(state_json.encode("utf-8"), replication))
        await asyncio.sleep(1)
        apply_updates(sync_mode, update_backlog, crdt, nreplicas)
        write_json(json_dir_name, i + 1, crdt.to_json())
        print(json.dumps(crdt.to_json(), indent=4))

    # be sure to catch every update
    await asyncio.sleep(7)
    apply_updates(sync_mode, update_backlog, crdt, nreplicas)
    write_json(json_dir_name, "final", crdt.to_json())
    print(json.dumps(crdt.to_json(), indent=4))
    print(update_backlog)
    print("7 sec over")
    await server_context.shutdown()
    logging.info(f'Ending simulation with name {name} repeat {nrepeat} at timestamp {time.time()}')

def write_json(json_dir_name: str, step, content):
    with open(f"{json_dir_name}/step-{step}.json", "w") as f:
        json.dump(content, f, indent=4)

def apply_updates(sync_mode: str, update_backlog: List[Any], crdt: CompoundCrdt, nreplicas: int):
    while len(update_backlog) > 0:
        if sync_mode == "operation":
            remote_update = update_backlog.pop()
            print(remote_update)
            crdt.apply_update(UpdateEvent.from_json(remote_update))
        elif sync_mode == "state":
            remote_state = update_backlog.pop()
            crdt.merge(CompoundCrdt.from_json(remote_state, nreplicas))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("request_mode")
    parser.add_argument("sync_mode")
    parser.add_argument("name")
    parser.add_argument("nrepeats")
    parser.add_argument("replication_id")
    parser.add_argument("replication_addrs", nargs='+')
    args = parser.parse_args()
    asyncio.run(run_single_simulation(args.request_mode, args.sync_mode, args.replication_addrs, int(args.replication_id), args.name, int(args.nrepeats)))