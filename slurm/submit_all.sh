#!/bin/bash
# submit_all.sh — One-click: generate inputs -> batch run -> collect results
# Usage:
#   export TURBINE_PROJ="$HOME/turbine_project_Yuan"   # or path to this repo
#   export TURBINE_N_RUNS=80
#   bash slurm/submit_all.sh

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=/dev/null
source "${SCRIPT_DIR}/config.sh"

cd "${TURBINE_PROJ}"
mkdir -p log inputs results sim_outputs

export TURBINE_N_RUNS
export TURBINE_PROJ

# Step 1: Generate LHS input parameters
JOB1=$(sbatch --parsable --export=ALL "${SCRIPT_DIR}/gen_inputs.sh")
echo "[1/3] gen_inputs  submitted (Job $JOB1)  N=${TURBINE_N_RUNS}"

# Step 2: Parallel simulations (array up to SLURM_ARRAY_MAX; extras exit early in batch_run.m)
JOB2=$(sbatch --parsable --dependency=afterok:"${JOB1}" --export=ALL "${SCRIPT_DIR}/batch_run.sh")
echo "[2/3] batch_run   submitted (Job $JOB2, array 1-${SLURM_ARRAY_MAX})"

# Step 3: Collect results (waits for all array tasks)
JOB3=$(sbatch --parsable --dependency=afterok:"${JOB2}" --export=ALL "${SCRIPT_DIR}/collect_results.sh")
echo "[3/3] collect     submitted (Job $JOB3)"

echo ""
echo "Pipeline: ${JOB1} -> ${JOB2}_[1-${SLURM_ARRAY_MAX}] -> ${JOB3}"
echo "PROJ=${TURBINE_PROJ}  N_RUNS=${TURBINE_N_RUNS}"
echo "Monitor:  squeue -u ${USER}"
echo "Results:  ${TURBINE_PROJ}/results/summary.csv"
