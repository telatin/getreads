# Installing `getreads`

Thanks to the ability of [Nextflow](https://www.nextflow.io/) to fetch the dependencies and the pipeline itself,
you will need to install Nextflow and one of the supported dependency engines:
* Docker (recommended if already installed)
* Conda (recommended if you don't have Docker)
* Singularity (for use in offline clusters)

## Installing Nextflow

If you don't have [Nextflow](https://www.nextflow.io/) installed:

1. Ensure you have Java 11 or higher installed:

```bash
java -version 
```

2. Create your binary package:

```bash
curl -s https://get.nextflow.io | bash
# will place ./nextflow in your current directory
```

3. Move the package in a directory in your `$PATH`:

```bash
# An example if you are in the sudoers
sudo mv nextflow /usr/local/bin

# ...or if you are not
mkdir -p "$HOME"/bin
mv nextflow "$HOME"/bin
export PATH="$PATH":"$HOME"/bin
echo "export PATH=$PATH:$HOME/bin" >> "$HOME"/.bashrc
```

## Running with Docker

If you already have [Docker](https://docs.docker.com/engine/install/)
installed (check with `docker --version`),
you can use the pipeline with the `-profile docker` option,
which is the recommended way:

```bash
nextflow run telatin/getreads -profile docker -r main \
  --list list.txt --outdir reads/ 
```

:bulb: Double dash parameters are for the pipeline itself, single dashed are for the Nextflow executor.

## Installing Miniconda and using conda

If you don't have [Miniconda](https://docs.conda.io/en/latest/miniconda.html) installed, you can install it as [described here](https://telatin.github.io/microbiome-bioinformatics/Install-Miniconda/).

Once you have Miniconda installed, you can run the pipeline with the `-profile conda` option:

```bash
nextflow run telatin/getreads -profile conda -r main\
  --list list.txt --outdir reads/ 
```

## Running with Singularity

If you have [Singularity](https://sylabs.io/guides/3.5/user-guide/) installed (check with `singularity --version`), use `-profile singularity`. 

You will need online access to download the Singularity image from Docker Hub, but once you have it, you can run the pipeline in offline mode.

To manually fetch the image, run:

```bash
# Download the image to a convenient location specified with --name
singularity pull --name "getreads.img"  docker://andreatelatin/getreads:2.0
```

To manually feed the image:
```bash
# Assuming the image path is $PATH_TO_SIF
nextflow run getreads/main.nf -with-singularity $PATH_TO_SIF \
  --list list.txt --outdir reads/ 
```


## Manual installation

You can clone the repository to have an easier way to modify the pipeline.
In this example we will clone the repository and create a permanent conda environment using mamba (see [here](https://telatin.github.io/microbiome-bioinformatics/Install-Miniconda/)):

One time steps:
```bash
# Clone the repository in a convenient location
git clone https://github.com/telatin/getreads.git

# Generate an environment with the required dependencies
mamba create -n getreads getreads/deps/env.yaml
```

Pipeline execution
```bash
# Activate the environment
conda activate getreads
# Run the pipeline (no profile needed)
nextflow run path_to/getreads/main.nf \
  --list list.txt --outdir reads/ 
```