#!/bin/bash

# Usage: ./run_simulation.sh <replication_id> <replication_addr1> <replication_addr2> ...

# Check at least 2 arguments (1 replication_id + at least 1 addr)
if [ "$#" -lt 2 ]; then
    echo "Usage: $0 <replication_id> <replication_addr1> [replication_addr2 ...]"
    exit 1
fi

replication_id=$1
shift
replication_addrs=("$@")

# Join replication addresses into a single string
replication_addrs_str="${replication_addrs[*]}"

# Function to run simulations
run_simulations() {
    mode=$1
    type=$2
    label=$3

    source .venv/bin/activate

    for ((nrepeat=0; nrepeat<25; nrepeat++)); do
        echo "Running: python3 singlesimulation.py $mode $type $label $nrepeat $replication_id ${replication_addrs_str}"
        python3 singlesimulation.py "$mode" "$type" "$label" "$nrepeat" "$replication_id" ${replication_addrs[@]}
        sleep 5
    done
}

# Run the 4 types of simulations
run_simulations "con" "operation" "CON-op-based"
run_simulations "non" "operation" "NON-op-based"
run_simulations "con" "state" "CON-state-based"
run_simulations "non" "state" "NON-state-based"