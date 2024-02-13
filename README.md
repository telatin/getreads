<a href="#readme" description="GetReads Repository">
<img align="right" width="128" height="128" src="docs/getreads-logo.png"></a>

# getreads [unsupported]

> [!NOTE]
> I recommend using [**nf-core/fetchngs**](https://github.com/nf-core/fetchngs)
> This repository is **no longer supported** as of 2023


A minimal pipeline to download FASTQ files from SRA given
a list of accession IDs.

## :magic_wand: Usage

See [installation](docs/INSTALLATION.md) for more details

```bash
# Suggestion: replace main with a version from the releases 
  nextflow run telatin/getreads -r main   -profile docker \
     --list list.txt --outdir downloaded-reads/
```

Where:

* `--list "list.txt"` is a list of SRA accession IDs in simple text format
* `--outdir "name"` is the name of the output directory
* `--wait INT` is the number of seconds to wait after running _ffq_ [default: 2]

* `-profile docker` will used Docker for dependencies. An easy alternative is to create a conda environment using `deps/env.yaml`. Singularity is supported but untested (usually clusters with singularity are offline anyway)
  
## :open_file_folder: Output

The output directory contains:

* :file_folder: **json** (JSON file, one for each accession)
* :file_folder: **urls** (text files with the download URIs)
* :file_folder: **reads** (FASTQ.gz files, a set per accession)
* :spiral_notepad: **stats.txt** (reads statistics)
* :spiral_notepad: **check.txt** (a report of number of files per ID downloaded, with control of number of reads per file being equal)
* :spiral_notepad: **table.tsv** metadata table from JSON files (only for samples where _ffq_ didn't fail) (_new in 2.0_)

## Alternatives

**[nf-core/fetchngs :star:](https://github.com/nf-core/fetchngs/)** is a fully-featured
pipeline to download reads and associated metadata. It's a fantastic and regularly
update tool.
Since sometimes it failed for me for reasons related to its complexity,
I made this minimal pipeline as a backup plan.

## Uses

* [ffq](https://github.com/pachterlab/ffq) to fetch URLs given the accessions, wrapped in _ffq-sake.py_ that retries if NCBI responds with "too many requests", but gracefully fails on 400 error.
* [wget](https://github.com/mirror/wget) to download the reads
* [seqfu](https://github.com/telatin/seqfu2) to collect stats

## Screenshot

![Screenshot](docs/imgs/carbon.svg)

* [Notes](test/README.md)
* [Releases](docs/RELEASES.md)


## Cite

If you use this pipeline, please cite:

* Gálvez-Merchán, Á., et al. (2023). *Metadata retrieval from sequence databases with ffq*. [Bioinformatics](https://doi.org/10.1093/bioinformatics/btac667)
* Telatin, A., et al. (2020). *SeqFu: A Suite of Utilities for the Robust and Reproducible Manipulation of Sequence File*s. [Bioengineering](https://doi.org/10.3390/bioengineering8050059)

