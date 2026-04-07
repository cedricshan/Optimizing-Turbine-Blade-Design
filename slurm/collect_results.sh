#!/bin/bash
#SBATCH --job-name=turbine_collect
#SBATCH --output=log/%x_%j.out
#SBATCH --error=log/%x_%j.err
#SBATCH --mem=2G
#SBATCH --time=00:10:00
#SBATCH -p common

set -euo pipefail

TURBINE_PROJ="${TURBINE_PROJ:-/hpc/home/rx67/turbine_project_Yuan}"
cd "${TURBINE_PROJ}"

echo "Collecting results at $(date) in ${TURBINE_PROJ}"
module load Matlab/R2022b
matlab -batch "addpath('scripts'); collect_results"
echo "Done at $(date)"
