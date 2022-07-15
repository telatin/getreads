/* 
 *   A minimal get reads program
 *   -----------------------------------------

/* 
 *   Input parameters 
 */
nextflow.enable.dsl = 2
params.list = "test/list.txt"
params.wait = 2
params.queue = false
params.debug = false

include { URLS; WGET; COLLECT; SPLIT; CHECK; TABLE } from './modules/misc'
include { FFQ; FFQLIST } from './modules/ffq'
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
         GetReads (version 1)
         ===================================
         list         : ${params.list}
         outdir       : ${params.outdir}
         wait         : ${params.wait} s
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
    FFQ(ids, params.wait)
    URLS(FFQ.out)
    SPLIT(URLS.out)
    urls = (SPLIT.out).transpose()
    

    if (params.debug) {
        urls.view()
    }
    
    WGET(urls)
    STATS(WGET.out)
    COLLECT(STATS.out.map{it -> it[1]}.collect())
    CHECK(COLLECT.out, file(params.list, checkIfExists: true))
    TABLE(FFQ.out.collect())
}