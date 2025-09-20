import argparse
import asyncio
from typing import List

from singlesimulation import run_single_simulation


async def simulation(replication_addrs: List[str], replication_id):
    for nrepeat in range(30):
        await run_single_simulation("con", "operation", replication_addrs, replication_id, "CON-op-based", nrepeat)
    for nrepeat in range(30):
        await run_single_simulation("non", "operation", replication_addrs, replication_id, "NON-op-based", nrepeat)
    for nrepeat in range(30):
        await run_single_simulation("con", "state", replication_addrs, replication_id, "CON-state-based", nrepeat)
    for nrepeat in range(30):
        await run_single_simulation("non", "state", replication_addrs, replication_id, "NON-state-based", nrepeat)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("replication_id")
    parser.add_argument("replication_1_addr")
    parser.add_argument("replication_2_addr")
    args = parser.parse_args()
    asyncio.run(run_single_simulation("non", "state", [args.replication_1_addr, args.replication_2_addr], int(args.replication_id), "testsim-run1", 1))