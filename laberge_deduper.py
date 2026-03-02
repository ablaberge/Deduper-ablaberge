#!/usr/bin/env python

import argparse
import re
import subprocess
import sys

def get_args():
    parser = argparse.ArgumentParser(
        description="Program to remove PCR duplicates from a sorted (chrom, pos) SAM file")
    parser.add_argument("-f", "--file",
                        help="Absolute path to the sorted SAM file for deduplication", type=str, required=True)
    parser.add_argument("-o", "--outfile",
                        help="Absolute path to deduplicated output SAM", type=str, required=True)
    parser.add_argument("-u", "--umi",
                        help="Text file containing a list of known UMIs", type=str, required=True)
    parser.add_argument("-s", "--sort",
                        help="Input SAM is unsorted", action="store_true", required=False)
    return parser.parse_args()

def adjust_pos(cigar:str, pos:int, strand:bool) -> int:
    """Takes the left-most position int from a SAM record and returns the true 5' start position adjusted for any soft-clipping"""
   
    cigar_pattern = r'(\d+)(\w)'
    cigar_blocks = re.findall(cigar_pattern, cigar)
    true_pos:int = pos

    if strand: # Reverse strand 
        for block in cigar_blocks:
            if block[1] in ("D", "M", "N"): # Check for deletions, matches, skips because these consume reference
                true_pos += int(block[0])
        if cigar_blocks[-1][1] == "S": # Check for soft clipping at the end of the cigar 
            true_pos += int(cigar_blocks[-1][0]) # Handle by adding to pos
    else:   # Forward strand
        if cigar_blocks[0][1] == "S":
            true_pos -= int(cigar_blocks[0][0])
    return true_pos

        

def extract_metadata(line:list) -> list:
    """Extracts chromosome, position, strand, and CIGAR from a SAM record"""
    chrom:str = line[2]
    pos:int = int(line[3])
    if int(line[1]) & 16:
        strand:bool = True
    else:
        strand:bool = False
    cigar:str = line[5]
    return [chrom,pos,strand,cigar]

def sort_sam(sam:str) -> str:
    """Sorts the input SAM file if user indicates it wasn't presorted"""
    sorted_sam:str = sam.split(".sam")[0]
    sorted_sam = f"{sorted_sam}.sorted.sam"
    subprocess.run(
        f"samtools sort -o {sorted_sam} {sam}",
        shell=True,
        check=True #raises an error if this fails
    )
    return sorted_sam

def check_sort_status(sam:str) -> bool:
    """Checks if the input SAM is sorted"""
    # Extract sort order from SAM
    result = subprocess.run(
        f"SORT_ORDER = $(samtools view -H {sam} | grep '@HD' | grep -o 'SO:[a-zA-Z]*' | cut -d':' -f2)",
        shell=True,
        check=True,
        capture_output=True,
        text=True
    )
    sort_order = result.stdout.strip() # Get sort status into python usable var
    return sort_order in ("coordinate", "queryname") # Returns true if sorted by coordinate, position, false otherwise



def main():

    args = get_args()
    metadata: set = set()     # Values = {UMI, pos, strand}, don't need to worry about chrom because we clear dict after encountering a new chrom
    umi: set = set()           # To hold known UMIs
    num_dupes_removed: int = 0
    num_headers: int = 0 
    num_unique_reads = 0
    num_wrong_umis = 0

    if args.sort: # Sort SAM before continuing
        print(f"Input SAM is unsorted. Sorting with Samtools now.")
        args.file = sort_sam(args.file)
        print(f"Path to sorted sam file: {args.file}")
    else: # User indicates SAM is already sorted, so make sure this is true or error out
        if not check_sort_status(args.file):
            print(f"Input SAM file is not sorted by coordinate and position. Please rerun and include '-s' flag for proper processing.")
            sys.exit(1)



    with open(args.umi, "r") as fh:
        for line in fh:
            umi.add(line.strip())

    curr_chrom: str = ""
    curr_pos: int = -1
    curr_umi: str = ""
    curr_strand: bool = False   # FALSE = forward, TRUE = reverse 
    cigar: str = ""
    firstRecordSeen: bool = False # Makes sure that we set ref_chrom when we hit the first record 
    ref_chrom: str = ""

    outfile = open(args.outfile, "w")

    with open(args.file, "r") as fh:
        for fullLine in fh:
            if fullLine.startswith("@"): # Handle header lines by writing them directly to outfile
                outfile.write(fullLine)
                num_headers += 1
                continue

            line = fullLine.strip().split()
            curr_umi = line[0].split(":")[-1]

            if curr_umi not in umi: # Not a known UMI, ignore this line
                num_wrong_umis += 1
                continue
            
            meta = extract_metadata(line)
            curr_chrom = meta[0]

            if not firstRecordSeen: # Seed reference chromosome that we will use to clear metadata dict after each chrom
                ref_chrom = curr_chrom
                firstRecordSeen = True
            
            if ref_chrom != curr_chrom:
                metadata = set()  # Reset metadata to save memory and search time 
                ref_chrom = curr_chrom # Set new reference chrom

            curr_pos = meta[1]
            curr_strand = meta[2]
            cigar = meta[3]
            curr_pos = adjust_pos(cigar, curr_pos, curr_strand) # Get true 5' start pos 
            if (curr_umi,curr_pos,curr_strand) not in metadata: # This is NOT a PCR duplicate
                metadata.add((curr_umi,curr_pos,curr_strand))
                outfile.write(fullLine)
                num_unique_reads += 1
            else:
                num_dupes_removed += 1

    # Print path to outputted SAM
    outfile.close()

    stats_file:str = args.outfile.split(".sam")[0]
    stats_file = stats_file + ".stats.txt"
    with open(stats_file, "w") as file:
        file.write(f"Path to deduplicated SAM file: {args.outfile}")
        file.write(f"Number of header lines: {num_headers}")
        file.write(f"Number of unique reads: {num_unique_reads}")
        file.write(f"Number of wrong UMIs encountered: {num_wrong_umis}")
        file.write(f"Number of duplicates removed: {num_dupes_removed}")
    print(f"Path to deduplicated SAM file: {args.outfile}")
    print(f"Path to stats file: {stats_file}")

if __name__ == "__main__":
    main()