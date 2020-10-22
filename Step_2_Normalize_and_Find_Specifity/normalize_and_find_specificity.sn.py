from snakelib import getsradata
import json
import time
import random
import os

# Some file systems (like ours), update slowly. This can cause snamake errors
# for job that finish quickly as the out files can appear newer than the input files. 
shell.prefix(" sleep $[ ( $RANDOM % 10 )  + 10 ] ; ")

# Get data from the config file. 
configfile: "config.json"

# Downloaded from ensembl, but renamed for easy access via wildcard.
GTF_PATH = "../../data/DATA_FOR_DATABASE/GTF_JSON_files/%s.83.gtf.json"

UGA_ENSEMBL_RELATIONS = "STATIC_FILES/UGAHash_Ensembl_ID_Equivalence_Tables/Ensembl_83_%s_sequence_set.txt.noexons.tsv"


# Rule paths and file names --------------------------------------------------
HTSEQ_COUNTS_PASSED_FOLDER = "HTSeqCounts_Passed_Cutoff/"
HTSEQ_COUNTS_PASSED_FILE   = "{seq_type}_{tax_id}/*.tsv"

BETWEEN_SAMPLE_NORMAL_CNTS_FOLDER = "DESeq2_Between-Sample_Normalized_Counts/"
BETWEEN_SAMPLE_NORMAL_CNTS_FILE   = "{seq_type}_{tax_id}_between-sample_normalized_counts.tsv"

SEQ_LEN_NORMAL_CNTS_FOLDER = "Seq_Len_Normalization/"
SEQ_LEN_NORMAL_CNTS_FILE   = "{seq_type}_{tax_id}_len_normalized.tsv"

EXPRESSION_TABLE_FOLDER = "Expression_Database_Tables/"
EXPRESSION_TABLE_FILE   = "{seq_type}_{tax_id}_expression_table.tsv"

SPECIFICTY_FOLDER = "Calc_Expression_Specificity/"
SPECIFICTY_FILES  = "{seq_type}_{tax_id}_specificity.tsv"

SPECIFICTY_TABLE_FOLDER = "Specificty_Database_Tables/"
SPECIFICTY_TABLE_FILES  = "{seq_type}_{tax_id}_specificity_table.tsv"

# Build targets --------------------------------------------------------------
seq_types = ["genes", "transcripts"]
tax_ids   = ["9606"]


# The end result is two tables, that will be inserted into the relational database.
rule all:
    input: 
        expand(
            SPECIFICTY_TABLE_FOLDER + SPECIFICTY_TABLE_FILES,
            tax_id=tax_ids, 
            seq_type=seq_types
        ), 
        expand(
            EXPRESSION_TABLE_FOLDER + EXPRESSION_TABLE_FILE,
            tax_id=tax_ids, 
            seq_type=seq_types
        )


"""
Between_Sample_Normalization preforms between sample normalization on some set of counts output 
by HTSeq-counts. However, we cannot move directly from HTSeq-counts as low-quality samples 
can cause errors in this process. For example, we need some set of transcripts or genes 
with non-zero counts across all conditions. Therefore, we removed all conditions with more 
than 75% zero counts. 
""" 
rule Between_Sample_Normalization: 
    input: 
        htseq_counts_tsvs = HTSEQ_COUNTS_PASSED_FOLDER + HTSEQ_COUNTS_PASSED_FOLDER 
    output:
        bs_normal_cnts = BETWEEN_SAMPLE_NORMAL_CNTS_FOLDER + BETWEEN_SAMPLE_NORMAL_CNTS_FILE 
    run:
        # Always check to see if output containing folder exists. 
        shell("mkdir -p %s" % HTSEQ_COUNTS_PASSED_FOLDER)

        # Load dat file and get link 
        shell("""
        Rscript custom_scripts/normalize_counts.R                                 \
            {htseq_counts_tsvs} # A glob of input tsv count files. \
            {bs_normal_cnts}    # The output path and file name     
        """)
        
"""
Sequence_Length_Normalization divides the normalized counts by their effective length so that the 
expression values of different genes and/or transcripts can be compared. This is similar to how 
FPKM is calculated, however, we skipped the step where the counts are divided by the total 
number of reads in the library. This was exclude as this would cause problems with the 
previous between-sample normalization step. 
"""
rule Sequence_Length_Normalization:
    input:
        bs_normal_cnts = BETWEEN_SAMPLE_NORMAL_CNTS_FOLDER + BETWEEN_SAMPLE_NORMAL_CNTS_FILE
    output:
       seq_len_normalization = SEQ_LEN_NORMAL_CNTS_FOLDER + SEQ_LEN_NORMAL_CNTS_FILE          
    run:
        # Always check to see if output containing folder exists. 
        shell("mkdir -p %s" % HTSEQ_COUNTS_PASSED_FOLDER)
        
        gtf_file = GTF_PATH % wildcards.tax_id
        
        # Load dat file and get link 
        shell("""
        python custom_scripts/calc_pseudoFPKM_from_count_matrix.py  \
            --deseq2   {input.bs_normal_cnts}                       \
            --gtf_json %s                                           \
            > {output.seq_len_normalization}
        """ % gtf_file )        

"""
This rule creates the expression table that simply lists the a null value, expression value, seq_id, and experiment_id. 
The null value is to indicate an auto-increment feild when inserting into the relational database (MySQL in this case).
"""
rule Create_Expression_Table:
    input:
        bs_normal_cnts = BETWEEN_SAMPLE_NORMAL_CNTS_FOLDER + BETWEEN_SAMPLE_NORMAL_CNTS_FILE
    output:
       expression_table = EXPRESSION_TABLE_FOLDER + EXPRESSION_TABLE_FILE  
    run:
        # Always check to see if output containing folder exists. 
        shell("mkdir -p %s" % HTSEQ_COUNTS_PASSED_FOLDER)
        
        uga_to_ensembl_ids = "STATIC_FILES/UGAHash_Ensembl_ID_Equivalence_Tables/Ensembl_83_%s_sequence_set.txt.noexons.tsv" % wildcards.tax_id 

        # Load dat file and get link 
        shell("""
        vectools join                       \
            --join_type INNER               \
            -1 0                            \
            -2 1                            \
            --base_matrix {normalized_vals} \
            %s                              \
        | vectools slice                    \
            --keep-cols 3,2,1,5             \
            > {output.expression_table} 
        """ % uga_to_ensembl_ids )

"""
Calculate_Specificity is used to pre-calculate specificty values for the samples as 
it is much too time consuming to do this dynamically in the database. 
This outputs a table of sequence, experiment, and the type of specificty. 
"""
rule Calculate_Specificity:
    input:
        bs_normal_cnts = EXPRESSION_TABLE_FOLDER + EXPRESSION_TABLE_FILE
    output:
        specificty_rels = SEQ_LEN_NORMAL_CNTS_FOLDER + SEQ_LEN_NORMAL_CNTS_FILE
    run:
        # Always check to see if output containing folder exists. 
        shell("mkdir -p %s" % SEQ_LEN_NORMAL_CNTS_FOLDER)
        
        # Load dat file and get link 
        shell("""
        python custom_scripts/generate_localization_relations.py           \
        --kb              knowledge_bases/kidney_anatomy.dl                \
        --rels            knowledge_bases/renaldb_logic_structures.dl      \
        --experiment_rels knowledge_bases/renaldb_experiments_knowledge.dl \
        --exps {input.bs_normal_cnts}                                      \
        > {output.specificty_rels} 
        """)


"""
This rule creates the expression table that simply lists the a null value, expression value, seq_id, and experiment_id. 
The null value is to indicate an auto-increment feild when inserting into the relational database (MySQL in this case).
"""
rule Create_Specificity_Table:
    input:
        specificty_rels = SEQ_LEN_NORMAL_CNTS_FOLDER + SEQ_LEN_NORMAL_CNTS_FILE
    output:
        specificty_table = SPECIFICTY_TABLE_FOLDER + SPECIFICTY_TABLE_FILES
    run:
        # Always check to see if output containing folder exists. 
        shell("mkdir -p %s" % SPECIFICTY_TABLE_FOLDER)

        # Load dat file and get link 
        uga_to_ensembl_ids = "STATIC_FILES/UGAHash_Ensembl_ID_Equivalence_Tables/Ensembl_83_%s_sequence_set.txt.noexons.tsv" % wildcards.tax_id

        # Load dat file and get link 
        shell("""
        vectools join                             \
            --join_type INNER                     \
            -1 0                                  \
            -2 1                                  \
            --base_matrix {input.specificty_rels} \
            %s                                    \
        | vectools slice                          \
            --keep-cols 3,2,1,5                   \
            > {output.specificty_table} 
        """ % uga_to_ensembl_ids )


