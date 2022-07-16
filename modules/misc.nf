process VERSIONS {
    publishDir "$params.outdir/", 
        mode: 'copy'
    
    output:
    path("versions.txt")

    script:
    """
    seqfu version >> versions.txt
    """
}
    
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
        mode: 'copy',
        pattern: "check.*"


    
    input:
    path("stats.txt")
    path("list.txt")

    output:
    path("check.*")
    path("*.fastq"), emit: fastq optional true

    script:
    """
    check.py --stats stats.txt --list list.txt --rescue --verbose > check.txt 2> check.log
    """

}

process GZIP {
    publishDir "$params.outdir/reads/", 
            mode: 'copy',
            pattern: "*.gz" 
    input:
    path(sym_zip)

    output:
    path("*.gz")

    script:
    real_zip = "readlink -f ${sym_zip}"
    """
    gzip -f "\$(${real_zip})" > "\$(basename ${sym_zip}).gz"
    """
}
process TABLE {
    publishDir "$params.outdir/", 
        mode: 'copy'
    
    input:
    path("*")

    output:
    path("table.tsv"), emit: table optional true
    path("*.gz"), emit: reads      optional true

    script:
    """
    table.py *.json > table.tsv
    """

}
