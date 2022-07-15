
process FFQLIST  {
    tag "$id(${sleep}s)"
    label "error_retry"
    publishDir "$params.outdir/json/", 
        mode: 'copy'
    
    input:
    path(list)
    
    
    output:
    tuple val(id), path("*.json")

    script:
    """
    cat "$list" | xargs ffq --split 
    """
}


process FFQ  {
    tag "$id(${sleep}s)"
    label "error_retry"
    publishDir "$params.outdir/json/", 
        mode: 'copy'
    
    input:
    val id
    val sleep
    
    
    output:
    tuple val(id), path("*.json") optional true

    script:
    """
    # ffq-sake will not die if ffq fails, but will retry on error 429 (rate limit),
    # while aborting on error 400 (bad request)
    # at each new attempt a pause of attempts*sleep is inserted

    ffq-sake.py $id  --retry 6 --pause $sleep --verbose 2>&1 > "${id}.log"
    """
}

process FFQ_V1  {
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


process FFQ_NORETRY  {
    tag "$id(${sleep}s)"
    label "error_retry"
    publishDir "$params.outdir/json/", 
        mode: 'copy'
    
    input:
    val id
    val sleep
    
    
    output:
    tuple val(id), path("*.json"), optional: true

    script:
    """
    ffq "$id" > "${id}.json"
    sleep $sleep
    """
}