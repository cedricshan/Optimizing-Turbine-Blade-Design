#!/bin/bash
#SBATCH --job-name=turbine_batch
#SBATCH --output=log/%x_%A_%a.out
#SBATCH --error=log/%x_%A_%a.err
#SBATCH --array=1-300%40
#SBATCH --mem=4G
#SBATCH --time=00:30:00
#SBATCH -p common

set -euo pipefail

TURBINE_PROJ="${TURBINE_PROJ:-/hpc/home/rx67/turbine_project_Yuan}"
cd "${TURBINE_PROJ}"

echo "Array task ${SLURM_ARRAY_TASK_ID} started at $(date) on $(hostname)  PROJ=${TURBINE_PROJ}"
module load Matlab/R2022b
matlab -batch "addpath('scripts'); batch_run"
echo "Array task ${SLURM_ARRAY_TASK_ID} finished at $(date)"
