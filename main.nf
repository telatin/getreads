/* 
 *   A minimal get reads program
 *   -----------------------------------------

/* 
 *   Input parameters 
 */
nextflow.enable.dsl = 2
params.list = "list.txt"
params.outdir = "$baseDir/reads"

include { URLS; WGET; COLLECT } from './modules/misc'
include { FFQ } from './modules/ffq'
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
    
// prints to the screen and to the log
log.info """
         GetReads (version 1)
         ===================================
         list         : ${params.list}
         outdir       : ${params.outdir}
         """
         .stripIndent()

workflow {
    FFQ(ids)
    URLS(FFQ.out)
    WGET(URLS.out)
    STATS(WGET.out.collect())
    COLLECT(STATS.out.map{it -> it[1]}.collect())
}