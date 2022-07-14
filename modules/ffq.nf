
process FFQ  {
    tag "$id"
    publishDir "$params.outdir/json/", 
        mode: 'copy'
    
    input:
    val id
    
    
    output:
    tuple val(id), path("*.json")

    script:
    """
    ffq "$id" > "${id}.json"
    """
}
