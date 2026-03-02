#!/bin/bash

#SBATCH --account=bgmp                    #REQUIRED: which account to use
#SBATCH --partition=bgmp                  #REQUIRED: which partition to use
#SBATCH --cpus-per-task=8                #optional: number of cpus, default is 1
#SBATCH --time=6:00:00               
#SBATCH --mem=20GB                        #optional: amount of memory, default is 4GB per cpu
#SBATCH --job-name=dedupe            #optional: job name
#SBATCH --output=LOG/dedupe_%j.out       #optional: file to store stdout from job, %j adds the assigned jobID
#SBATCH --error=LOG/dedupe_%j.err        #optional: file to store stderr from job, %j adds the assigned jobID

SCRIPT="./laberge_deduper.py"
SAM="C1_SE_uniqAlign.sorted.sam"
OUTPUT="C1_SE_uniqAlign.sorted.deduped.sam"
UMI="STL96.txt"

/usr/bin/time -v "$SCRIPT" -f "$SAM" \
    -o "$OUTPUT" \
    -u "$UMI"