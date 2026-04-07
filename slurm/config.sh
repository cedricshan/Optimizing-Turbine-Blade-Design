# Source from other Slurm scripts: `source "$(dirname "$0")/config.sh"`
# Override before submit: export TURBINE_PROJ=/path/to/project TURBINE_N_RUNS=80

: "${TURBINE_PROJ:=${HOME}/turbine_project_Yuan}"
: "${TURBINE_N_RUNS:=80}"
: "${SLURM_ARRAY_MAX:=300}"
