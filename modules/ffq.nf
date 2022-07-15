
process FFQ  {
    tag "$id(${sleep}s)"
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
