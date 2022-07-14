FROM nfcore/base:1.9
LABEL authors="Andrea Telatin" \
      description="getreads container"

# Install the conda environment
COPY env.yaml /environment.yml
RUN conda env create -n env -f /environment.yml && conda clean -a

# Add conda installation dir to PATH (as 'conda activate')
ENV PATH /opt/conda/envs/env/bin:$PATH

# Dump the details for reproducibility
RUN conda env export --name env > workflow.yml