# Deduper

## Description

This tool removes PCR duplicates from single-end DNA sequencing libraries and retains only a single copy of each read (the first encountered read). Records with erroneous UMIs with are discarded. Records are considered PCR duplicates if and only if all of the following fields are consistent between multiple records: UMI, strand, 5' start position, and chromosome (RNAME). 


## Requirements

### Input 

The SAM file must:
- Contain only uniquely mapped single-end reads
- Be sorted by chromosome and position OR call to script must include ```-s``` flag 
- UMI must be the final set of characters in each record's QNAME (e.g., ```NS500451:154:HWKTMBGXX:1:11101:15364:1139:GAACAGGT```) 

The UMI file must:
- Be a text file
- Contain one UMI per line

### Resources 

This script loads one chromosome at a time into memory, so you must have enough memory to store the length of the largest chromosome in your input SAM file. Additionally, if using the ```-s``` flag, a minimum of 716 MiB is required. 


### Dependencies 

Python 3.12.10
Samtools 1.22.1


## Usage 

Description of parameters:

    - ```-f```, ```--file```: designates absolute file path to sorted sam file, REQUIRED
    - ```-o```, ```--outfile```: designates absolute file path to deduplicated sam file, REQUIRED
    - ```-u```, ```--umi```: designates file containing the list of UMIs, REQUIRED
    - ```-s```, ```--sort```: indicates that input sam file is NOT sorted, OPTIONAL 
    - ```-h```, ```--help```: prints a help message


There are two ways to run the tool:

1. With run_deduper.sh 
- Adjust Slurm settings at the top of the script for your hpc/computer 
- Adjust global variables SAM, OUTPUT, and UMI to include paths to your input SAM, output SAM, and UMI text file
- Run the following command: ```./run_deduper.sh```

2. With python script directly 
- Run the following command: ```./laberge_deduper.py -f [path to input SAM] -o [path to output] -u [path to UMI text file]```
- ```-s``` flag MUST be included in the command if input SAM is unsorted

Outputs:

- Chromosome and position sorted SAM file (only if ```-s``` flag is used)
- Deduplicated SAM file
- Stats file containing information about the records removed  