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

process SPLIT {
    tag "$id"
    
    input:
    tuple val(id), path(file)  

    output:
    tuple val(id), file("${id}_*")

    script:
    """
    split -l 1 ${file} ${id}_
    """
}
process WGET {
    tag "$id"

    publishDir "$params.outdir/reads/", 
        mode: 'copy'
    
    input:
    tuple val(id), path(file)  
    
    
    output:
    tuple val(id), file("*.gz")

    script:
    """
    cat "$file" | xargs wget 
    """
}

process COLLECT {
    publishDir "$params.outdir/", 
        mode: 'copy'
    
    input:
    file("*.stats")

    output:
    file("stats.txt")

    script:
    """
    cat *.stats | head -n 1 > stats.txt
    grep -v "Total bp" *.stats | cut -f 2 -d : | sort  >> stats.txt
    """
}