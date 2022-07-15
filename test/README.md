# Test directory

## Minimal test

From the repository root:

```bash
nextflow run main.nf --list test/list.txt --outdir test/out --resume
```

:warning: the test file contains 3 IDs, the last one can cause an error.

## Notes

Some IDs were never retrieved by _ffq_ including:

* SRR8907358 (failed with FFQ but appears OK on NCBI)

The error in this case was not "too many requests" but "400 Bad Request".
It appears that _ffq_ was requesting FASTA instead of FASTQ. 
The pipeline at the moment just skips these IDs.