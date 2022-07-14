
process STATS {
    tag "$id"

    input:
    tuple val(id), file(fastq)
    
    
    output:
    tuple val(id), path("*.stats")

    script:
    """
    seqfu stats ${fastq}  > ${id}.stats
    """
}