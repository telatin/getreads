
process STATS {
    
    tag "$id"

    input:
    tuple val(id), file("*.gz")
    
    
    output:
    path("${id}.stats")

    script:
    """
    seqfu stats *.gz > ${id}.stats
    """
}