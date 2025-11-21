/* 
 *   A minimal get reads program
 *   -----------------------------------------

/* 
 *   Input parameters 
 */
nextflow.enable.dsl = 2
params.list = "test/list.txt"
params.wait = 2
params.ignore = false
params.queue = false
params.debug = false
params.nostats = false

include { IS_ONLINE; URLS; WGET; COLLECT; SPLIT; CHECK; TABLE; GZIP } from './modules/misc'
include { FFQ; FFQLIST; FFQ_NORETRY} from './modules/ffq'
include { STATS } from './modules/seqfu'
/*
 *   DSL2 allows to reuse channels
 */

/*
 *   Function to validate accession list
 */
def validateAccessionList(listFile) {
    def validIds = []
    def lineNum = 0
    def warnings = []

    listFile.eachLine { line ->
        lineNum++
        def trimmed = line.trim()

        // Skip empty lines and comments
        if (trimmed.isEmpty() || trimmed.startsWith('#')) {
            return
        }

        // Check for spaces or tabs
        if (trimmed.contains(' ') || trimmed.contains('\t')) {
            warnings.add("Line ${lineNum}: Contains whitespace - using first token only: '${trimmed}'")
            // Try to use first token
            trimmed = trimmed.split(/\s+/)[0]
        }

        // Basic accession format check (SRR/ERR/DRR/SRX/ERX/DRX followed by digits)
        if (!trimmed.matches(/^[SED]R[RXPS]\d+$/)) {
            warnings.add("Line ${lineNum}: '${trimmed}' doesn't match expected accession format (e.g., SRR123456, ERR789012)")
        }

        // Check for duplicates
        if (validIds.contains(trimmed)) {
            warnings.add("Line ${lineNum}: Duplicate accession '${trimmed}' (will be processed only once)")
        } else {
            validIds.add(trimmed)
        }
    }

    // Print warnings
    if (warnings.size() > 0) {
        log.warn "=== Input Validation Warnings (${warnings.size()}) ==="
        warnings.each { log.warn "  - ${it}" }
        log.warn "=========================================="
    }

    log.info "Validated ${validIds.size()} unique accession(s) from ${lineNum} line(s)"

    return validIds
}



 
// check if params.list exists
if (!file(params.list).exists()) {
    log.error "ERROR: File ${params.list} does not exist (--list)"
    exit 1
}
// check if file is empty
if (file(params.list).size() == 0) {
    log.error "ERROR: File '${params.list}' is empty (--list)"
    exit 1
}

// Validate accession list and create channel
def validatedIds = validateAccessionList(file(params.list))

if (validatedIds.size() == 0) {
    log.error "ERROR: No valid accessions found in ${params.list}"
    exit 1
}

Channel
    .from(validatedIds)
    .set { ids }  

id_file = Channel
    .from(file(params.list, checkIfExists: true))

 
// prints to the screen and to the log
log.info """
         GetReads (version 3.1)
         ===================================
         list         : ${params.list}
         outdir       : ${params.outdir}
         wait         : attempt * ${params.wait} s

         [debug-ignore: ${params.ignore}]
         [resources   : ${params.max_cpus}; ${params.max_memory};${params.max_time}]
         """
         .stripIndent()


workflow SINGLE {
    /*
     TODO
    */
    take:
    id_file

    main:
    FFQLIST(id_file)

    emit:
    FFQLIST.out

}

workflow {
    // Check if pipeline is running online
    IS_ONLINE()

    // Get project metadata with FFQ "sake"
    if (params.ignore) {
        DATA = FFQ_NORETRY(ids, params.wait, IS_ONLINE.out)
    } else {
        DATA = FFQ(ids, params.wait, IS_ONLINE.out)
    }
 
    // Collect URIs
    URLS(DATA)
    SPLIT(URLS.out)
    urls = (SPLIT.out).transpose()
    

    if (params.debug) {
        urls.view()
    }
    WGET(urls)

    if (params.nostats == false) {
      STATS(WGET.out)
      COLLECT(STATS.out.map{it -> it[1]}.collect())
      CHECK(COLLECT.out, file(params.list, checkIfExists: true))
      //TABLE(FFQ.out.collect())
      GZIP((CHECK.out.fastq).flatten())
      TABLE(DATA.map{it -> it[1]}.collect())
    } 
}