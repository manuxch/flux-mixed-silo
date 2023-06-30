#!/bin/bash
#
#SBATCH --job-name=tilt-silo
#SBATCH --output=tilt-silo_%A_%a.out
#SBATCH --ntasks=1
#SBATCH --mem-per-cpu=128mb
#SBATCH --time=8-24:0:0
#SBATCH --array=0-__N__

echo "SLURM_JOBID: " $SLURM_JOBID
echo "SLURM_ARRAY_TASK_ID: " $SLURM_ARRAY_TASK_ID
echo "SLURM_ARRAY_JOB_ID: " $SLURM_ARRAY_JOB_ID

./tilt-silo params-$SLURM_ARRAY_TASK_ID.in

