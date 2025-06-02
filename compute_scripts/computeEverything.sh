#!/bin/bash
#SBATCH -n 1                                                        # Number of cores
#SBATCH -N 1                                                        # Ensure that all cores are on one machine
#SBATCH -t 92:00:00 #12:00:00 #1-0:00                                                   # Runtime in D-HH:MM, minimum of 10 minutes
#SBATCH -p blackhole #test # Partition to submit to
#SBATCH --mem=8G #60G #24G #                                                 # Memory pool for all cores (see also --mem-per-cpu)
#SBATCH -o logs/%j.out          # File to which STDOUT will be written, %j inserts jobid
#SBATCH -e logs/%j.err          # File to which STDERR will be written, %j inserts jobid
##SBATCH --mail-type=ALL                                             # Type of email notification- BEGIN,END,FAIL,ALL
##SBATCH --mail-user=hyerin.cho@cfa.harvard.edu                  # Email to which notifications will be sent

export OMP_NUM_THREADS=1

source ~/venv3/bin/activate

#python computeProfiles.py bigtorus_a.9_l128_g13by9_beta1
#python computeProfiles.py bigtorus_a.9_l192_g13by9_beta100
#python computeProfiles.py bigtorus_a.9_l64_g13b9_beta100
#python computeProfiles.py bigtorus_am9_l128_g13by9_beta1
#python computeProfiles.py bigtorus_am9_l192_g13by9_beta100
#python computeProfiles.py bigtorus_a.5_l128_g13by9_beta1
#python computeProfiles.py bigtorus_a.5_l192_g13by9_beta100
#python computeProfiles.py bigtorus_a.5_l64_g13by9_beta100
#python computeProfiles.py bigtorus_a0_l128_g13by9_beta1
#python computeProfiles.py bigtorus_a0_l192_g13by9_beta100
#python computeProfiles.py bigtorus_a0_l64_g13b9_beta100
