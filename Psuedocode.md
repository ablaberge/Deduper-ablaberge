
## Problem Definition 
We need an algorithm to removal PCR duplicates from a sequencing library by retaining only one copy of each read. We can identify true PCR duplicates by evaluating the chromosome, strand, position, and UMI of each sequence. Using this information, we can remove the neccesary number of duplicates *if and only if* these values are each equivalent in one or more other records. Importantly, we need to account for any soft clipping that occured during the alignment stage by checking the CIGAR string and adjusting position accordingly. 

## Examples
Test input/output SAM files in ```Test```.

```Test/readMe.md``` contains descriptions of each test case addressed.

## Pseudocode 

```
# NOTE: This algo assumes the input is an UNSORTED SAM file
metadata: dict = {}     # Key = UMI, Value = {chrom,strand,position}
umi: set = {}           # To hold known UMIs

Open STL96.txt for reading: 
    Read all known UMIs into umi 
    Close STL96.txt

curr_chrom: str = ""
curr_pos: int = ""
curr_umi: str = ""
curr_strand: bool = FALSE   # FALSE = forward, TRUE = reverse 
cigar: str = ""

Open input SAM for reading & open new output SAM for writing:
    While SAM has next line:
        If this line is a header line:
            Write line to output SAM
            Continue
        Else:
            curr_umi =  [extract from end of QNAME]
            If curr_umi not in umi:
                Continue
            curr_chrom = [extract from col 3]
            curr_pos =  [extract from column 4]
            curr_strand =  [extract from bit 16 of flag]
            cigar = [extract from column 6]
            If cigar contains 'nS' at the start (where n is some integer):
                If curr_strand is FALSE:    # We have a forward strand
                    curr_pos = curr_pos - n
            If metadata[umi] == {curr_chrom, curr_pos, curr_strand}:
                Continue    # This is a PCR duplicate 
            Else:
                Write line to output SAM

Print path to outputted SAM

```

## Functions

```
def adjust_pos(cigar:str, pos:int, strand:bool) -> int:
    '''Takes the left-most position int from a SAM record and returns the true 5' start position adjusted for any soft-clipping''
    return adjusted_pos

Input: 50M, 100, 0
Output: 100

Input: 50M5S, 100, 0
Output: 100

Input 5S50M, 100, 0
Output: 95

Input 5S50M, 100, 1
Output: 100

Input 50M5S, 100, 1
Output: 145
```

```
def extract_metadata(line:str) -> [int, int, bool]
'''Extracts chromosome, position, and strand from a SAM record'''
    return chrom, pos, strand

Input: 
NS500451:154:HWKTMBGXX:1:11101:1111:1111:AACCGGTT	0	1	1000	60	50M	*	0	0	ACGTACGTACGTACGTACGTACGTACGTACGTACGTACGTACGTACGTAC	IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII	MD:Z:50	NH:i:1

Output: [1, 1000, 0]

```
