
## Summary of test cases covered in input_test.sam and output_test.sam

**Duplicates Removed:**
- Case 1: 2 duplicates removed
    - Input: lines 5 - 7, Output: line 5
    - These 3 reads map to chr1, forward strand, position 1000, UMI: AACCGGTT
- Case 4: 1 duplicate removed
    - Input: line 10-11, Output: line 8
    - Flag 16 indicates reverse strand
    - Position 3000 on reverse strand, same UMI
- Case 6: 1 duplicate removed
    - Input: lines 14-15, Ouput: line 11
    - 5S45M means 5 bases soft clipped at start, mapped position is 5000
    - True 5' start is at 5000 (for forward) or 5000+45-1=5044 (for reverse)
- Case 8: 1 duplicate removed
    - Input: lines 18-19, Output: line 14
    - 20M100N30M means 20 match, 100 skipped (intron), 30 match
    - Position 7000, 5' end is at 7000 for forward strand

**Non-duplicates Kept:**
- Case 2: Different UMI
    - Input: line 8, Output: line 6
    - Same position but different UMI (TTGGCCAA vs AACCGGTT)
- Case 3: Different position
    - Input: line 9, Output: line 7
    - Same UMI but different position (1000 vs 2000)
- Case 5: Different strands (both forward and reverse at same position)
    - Input: lines 12-13, Output: lines 9-10
    - Forward strand at 4000 vs reverse strand at 4000
- Case 7: Different chromosomes
    - Input: lines 16-17, Output: lines 12-13
    - Same position but different chromosomes (chr1 vs chr2)
- Case 9: Unique read
    - Input: line 20, Output:line 15
