
process FFQ  {
    tag "$id"
    label "error_retry"
    publishDir "$params.outdir/json/", 
        mode: 'copy'
    
    input:
    val id
    val sleep
    
    
    output:
    tuple val(id), path("*.json")

    script:
    """
    ffq "$id" > "${id}.json"
    sleep $sleep
    """
}
