# getreads (aka ffq-sake)

A minimal pipeline to download FASTQ files from SRA given
a list of accession IDs.

## Usage

```bash
nextflow run andreatelatin/getreads -p docker --list list.txt --outdir sra
```

Where:
* `--list "list.txt"` is a list of SRA accession IDs in simple text format
* `--outdir "name"` is the name of the output directory
* `--wait INT` is the number of seconds to wait after running _ffq_ [default: 2]
* `--single` will run a single job for _ffq_ to reduce the queries to NCBI

## Output

The output directory contains:

* :folder: **json** (JSON file, one for each accession)
* :folder: **urls** (text files with the download URIs)
* :folder: **reads** (FASTQ.gz files, a set per accession)
* :file: **stats.txt** (reads statistics)


## Alternatives

**[nf-core/fetchngs](https://github.com/nf-core/fetchngs/)** is a fully-featured
pipeline to download reads and associated metadata. It's a fantastic and regularly
update tool.
Since sometimes it failed for me for reasons sometimes related to its complexity,
I made this minimal pipeline as a backup plan.