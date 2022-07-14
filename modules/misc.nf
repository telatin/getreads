process URLS {
    tag "$id"
    publishDir "$params.outdir/urls/", 
        mode: 'copy'
    
    input:
    tuple val(id), path(file)  
    
    
    output:
    tuple val(id), file("*.txt")

    script:
    """
    cat "$file" | jq ".\$(basename $file | cut -f 1 -d .).files.ftp[].url" > \$(basename $file | cut -f 1 -d .).txt
    """
}

process WGET {
    tag "$id"

    publishDir "$params.outdir/reads/", 
        mode: 'copy'
    
    input:
    tuple val(id), path(file)  
    
    
    output:
    tuple val(id), file("${id}*.gz")

    script:
    """
    cat "$file" | xargs wget
    """
}

process COLLECT {
    publishDir "$params.outdir/stats/", 
        mode: 'copy'
    
    input:
    file("*.stats")

    output:
    file("stats.txt")

    script:
    """
    head -n 1 *.stats | head -n 1 > stats.txt
    grep -v "Total bases" *.stats > stats.txt
    """
}