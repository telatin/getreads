# :arrow_down: getreads (aka *ffq-sake*)

A minimal pipeline to download FASTQ files from SRA given
a list of accession IDs.

## :magic_wand: Usage

```bash
nextflow run andreatelatin/getreads -p docker --list list.txt --outdir sra
```

Where:

* `--list "list.txt"` is a list of SRA accession IDs in simple text format
* `--outdir "name"` is the name of the output directory
* `--wait INT` is the number of seconds to wait after running _ffq_ [default: 2]
* `--single` will run a single job for _ffq_ to reduce the queries to NCBI

## :open_file_folder: Output

The output directory contains:

* :file_folder: **json** (JSON file, one for each accession)
* :file_folder: **urls** (text files with the download URIs)
* :file_folder: **reads** (FASTQ.gz files, a set per accession)
* :spiral_notepad: **stats.txt** (reads statistics)
* :spiral_notepad: **check.txt** (a report of number of files per ID downloaded, with control of number of reads per file being equal)

## Alternatives

**[nf-core/fetchngs :star:](https://github.com/nf-core/fetchngs/)** is a fully-featured
pipeline to download reads and associated metadata. It's a fantastic and regularly
update tool.
Since sometimes it failed for me for reasons related to its complexity,
I made this minimal pipeline as a backup plan.

## Uses

* [ffq](https://github.com/pachterlab/ffq) to fetch URLs given the accessions
* [wget](https://github.com/mirror/wget) to download the reads
* [seqfu](https://github.com/telatin/seqfu2) to collect stats
