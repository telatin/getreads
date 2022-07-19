## Version 1.0

```bash
mamba create -n getreads -c conda-forge -c bioconda  \
  wget ffq jq  \
  rich typer "seqfu>=1.0"
```
## Version 2.0

```bash
mamba create -n getreads -c conda-forge -c bioconda  \
  wget ffq jq \
  rich typer "seqfu>=1.0" \
  sra-tools
```
