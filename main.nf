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



 
// prints to the screen and to the log
log.info """
         GetReads (version 3.0)
         ===================================
         --list         : ${params.list}
         --outdir       : ${params.outdir}
         --wait         : attempt * ${params.wait} s

         [debug-ignore: ${params.ignore}]
         [resources   : ${params.max_cpus}; ${params.max_memory};${params.max_time}]
         """
         .stripIndent()

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


Channel
    .from(file(params.list, checkIfExists: true))
    .splitCsv(header:false, sep:'', strip:true)
    .map { it[0] }
    .unique()
    .set { ids }  

id_file = Channel
    .from(file(params.list, checkIfExists: true))

 
// prints to the screen and to the log
log.info """
         GetReads (version 3)
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