#!/bin/bash
#SBATCH --job-name=turbine_test
#SBATCH --output=log/%x_%j.out
#SBATCH --error=log/%x_%j.err
#SBATCH --mem=4G
#SBATCH --time=00:15:00
#SBATCH -p common

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=/dev/null
source "${SCRIPT_DIR}/config.sh"
cd "${TURBINE_PROJ}"

echo "Job started at $(date) on $(hostname)  PROJ=${TURBINE_PROJ}"
module load Matlab/R2022b
matlab -batch "addpath('scripts'); single_test"
echo "Job finished at $(date)"
