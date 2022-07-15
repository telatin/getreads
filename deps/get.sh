mamba create -n getreads -c conda-forge -c bioconda  \
  wget ffq jq sra-tools \
  rich typer "seqfu>=1.0"
