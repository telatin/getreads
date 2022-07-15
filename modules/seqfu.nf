
process STATS {
    tag "$id"

    input:
    tuple val(id), path(fastq)
    
    
    output:
    tuple val(id), path("*.stats")

    script:
    """
    seqfu stats ${fastq}  > ${id}.stats
    """
}