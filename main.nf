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

include { URLS; WGET; COLLECT; SPLIT; CHECK; TABLE; GZIP } from './modules/misc'
include { FFQ; FFQLIST; FFQ_NORETRY} from './modules/ffq'
include { STATS } from './modules/seqfu'
/* 
 *   DSL2 allows to reuse channels
 */

check_input = file(params.list, checkIfExists: true)
if (check_input.isEmpty()) {exit 1, "File provided with --list is empty: ${check_input.getName()}!"}


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
         GetReads (version 2)
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
    if (params.ignore) {
        DATA = FFQ_NORETRY(ids, params.wait)
    } else {
        DATA = FFQ(ids, params.wait)
    }
    //FFQ(ids, params.wait)
    //URLS(FFQ.out)
    URLS(DATA)
    SPLIT(URLS.out)
    urls = (SPLIT.out).transpose()
    

    if (params.debug) {
        urls.view()
    }
    
    WGET(urls)
    STATS(WGET.out)
    COLLECT(STATS.out.map{it -> it[1]}.collect())
    CHECK(COLLECT.out, file(params.list, checkIfExists: true))
    //TABLE(FFQ.out.collect())
    GZIP((CHECK.out.fastq).flatten())
    TABLE(DATA.map{it -> it[1]}.collect())
}