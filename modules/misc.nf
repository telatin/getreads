process URLS {
    tag "$id"
    publishDir "$params.outdir/urls/", 
        mode: 'copy'
    
    input:
    tuple val(id), path(jsonfile)  
    
    
    output:
    tuple val(id), file("*.txt")

    script:
    """
    cat "$jsonfile" | jq ".\$(basename $jsonfile | cut -f 1 -d .).files.ftp[].url" > \$(basename "$jsonfile" | cut -f 1 -d .).txt
    """
}

process SPLIT {
    tag "$id"
    
    input:
    tuple val(id), path(file)  

    output:
    tuple val(id), path("${id}_*")

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
    tuple val(id), path("*.gz")

    script:
    """
    echo \$(cat "$file")
    cat "$file" | xargs wget 
    """
}

process COLLECT {
    publishDir "$params.outdir/", 
        mode: 'copy'
    
    input:
    path("*.stats")

    output:
    path("stats.txt")

    script:
    """
    cat *.stats | head -n 1 > stats.txt
    grep -v "Total bp" *.stats | cut -f 2 -d : | sort  >> stats.txt
    """
}

process CHECK {
    publishDir "$params.outdir/", 
        mode: 'copy'
    
    input:
    path("stats.txt")
    path("list.txt")

    output:
    path("check.*")

    script:
    """
    check.py --stats stats.txt --list list.txt > check.txt 2> check.log
    """

}

process TABLE {
    publishDir "$params.outdir/", 
        mode: 'copy'
    
    input:
    path("*")

    output:
    path("table.tsv"), optional: true

    script:
    """
    table.py *.json > table.tsv
    """

}
