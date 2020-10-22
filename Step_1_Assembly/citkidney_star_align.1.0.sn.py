from snakelib import getsradata
# from srahelp import getftpfilesize
import json
import time
import os

# Some file systems (like ours), update slowly. This can cause snamake errors
# for job that finish quickly as the out files can appear newer than the input files. 
shell.prefix(" sleep $[ ( $RANDOM % 10 )  + 12 ] ; ")

# Get data from the config file. 
configfile: "config.json"

# Reference paths ------------------------------------------------------------
# These determine which reference sets will be used. 
VERSION    = config["VERSION"]
BASE_PATH  = config["BASE_PATH"]
INDEX_BASE = config["INDEX_BASE"]


# Rule paths and file names --------------------------------------------------

METADATA_FOLDER  = "METADATA/" 
METADATA_FILE    = "{sample}.json"

SRA_FOLDER       = "SRAs/"
SRA_FILE         = "{sample}.sra"

# FASTQDUMP_FILE_1 and FASTQDUMP_FILE_2 as some samples are paired end. 
FASTQDUMP_FOLDER = "FASTQs/"
FASTQDUMP_FILE_1 = "{sample}_1.fastq"
FASTQDUMP_FILE_2 = "{sample}_2.fastq"

# This is treated a bit differently as STAR outputs an entire folder. 
STAR_FOLDER      = "STAR_ASSEMBLIES/"
STAR_SAMPLE_DIR  = "{sample}/"
OUT_PREFIX       = STAR_SAMPLE_DIR + "sample_"
SAM              = STAR_SAMPLE_DIR + "sample_Aligned.sortedByCoord.out.bam"
TX_BAM           = STAR_SAMPLE_DIR + "sample_Aligned.toTranscriptome.out.bam"
TX_BAM_SORTED    = STAR_SAMPLE_DIR + "sample_Aligned.toTranscriptome.sortedByCoord.out.bam"
CHIM             = STAR_SAMPLE_DIR + "sample_Chimeric.out.junction"
LOG_OUT_FINAL    = STAR_SAMPLE_DIR + "sample_Log.final.out"
LOG_OUT          = STAR_SAMPLE_DIR + "sample_Log.out"
LOG_PROGRESS_OUT = STAR_SAMPLE_DIR + "sample_Log.progress.out"
OUT_TAB          = STAR_SAMPLE_DIR + "sample_SJ.out.tab"

HTSEQ_FOLDER     = "HTSeqTables/"
GENES_TABLE      = "{sample}.genes.tsv"
TRANSCRIPT_TABLE = "{sample}.transcripts.tsv"

# Build targets --------------------------------------------------------------
sample_dict = {}
DATASETS = []
for line in open(config["samples"]):
    DATASETS.append(line.strip())


# Start rules ----------------------------------------------------------------
# All file rules are included here for trouble shooting purposes. 
#In the cases of single end make blank transcripts file.
rule all:
    input: 
        #expand("METADATA/{sample}.dat.json", sample=DATASETS),
        #expand("SRAs/{sample}.sra", sample=DATASETS),
        #expand("FASTQs/{sample}_1.fastq", sample=DATASETS),
        #expand(OUT_PREFIX, sample=DATASETS)
        #expand(SAM, sample=DATASETS),
        #expand(LOG_OUT_FINAL, sample=DATASETS),
        #expand(LOG_OUT, sample=DATASETS),
        #expand(LOG_PROGRESS_OUT, sample=DATASETS),
        #expand(OUT_TAB, sample=DATASETS),
        expand(HTSEQ_FOLDER + GENES_TABLE, sample=DATASETS),
        expand(HTSEQ_FOLDER + TRANSCRIPT_TABLE, sample=DATASETS)

"""
The getmetadata rule downloads various metadata from NCBI regarding the SRA in question. 
This is used for determining various future steps in analysis such as to align the sample 
as a paired end of single end, etc. 
"""
rule getmetadata:
    output:
        metadata_out=METADATA_FOLDER + METADATA_FILE
    run:
        # If no folder exists, create the folder. 
        shell("mkdir -p %s ;" % METADATA_FOLDER)
        
        # Download and save metadata as a json file. 
        tmp_dict = getsradata.SRAXMLToJSON(wildcards.sample)
        json_txt = json.dumps(tmp_dict, sort_keys=True, indent=4, separators=(',', ': '))
        f_obj = open(output.metadata_out,'w')
        f_obj.write(json_txt)
        f_obj.close()
        
 
"""
The download sequence data rule downloads the SRA using the link stored in the METADATA. 
"""
rule downloadseqdata: 
    input: 
        metadata=METADATA_FOLDER + METADATA_FILE
    output:
        sra_out=SRA_FOLDER + SRA_FILE
    run:
        # If no folder exists, create the folder. 
        shell("mkdir -p %s ;" % SRA_FOLDER)

        # Load dat file and get link 
        json_obj = json.load(open(input.metadata))
        sra_run = json_obj["RUN_accession"]
        # ftp_link = json_obj["ftp_link"]        ## Source yet FTP link doens't work!
        # shell("wget --quiet  --random-wait  %s -O {output.sra_out}" % ftp_link)  ## See above comment
        shell("/disk2/Resources/software/sratoolkit.2.10.5-centos_linux64/bin/prefetch.2.10.5 %s -o {output.sra_out}" %sra_run)
       
        # --------------------- Error Checking -------------------------------
        # Get the size of the file from the FTP server, wget cannot tell us if the file 
        # downloaded perfectly, and since there are no checksums, just make sure the 
        # file sizes match.  

        # Wait a little bit to avoid errors with the file system updating slowly. 
        time.sleep(0.5)
        
        # # Get size from FTP 
        # from_ftp = getftpfilesize(ftp_link)
        # # Get size on disc. 
        # on_disc  = os.path.getsize(output.sra_out)
          
        # # Fail if file sizes to not match.  
        # assert from_ftp == on_disc
 

"""
The fastqdump rule simply extracts the fastq files from the SRA files. 
Fastq files are large, so these are deleted when the rules calling fastqdump are finished.

Links trouble shooting the problem: 
https://edwards.sdsu.edu/research/fastq-dump/
https://www.biostars.org/p/156909/
I have no idea why -M 0 keeps the lines equal but it does. 
Nevermind -M 0 allows for sequences short enought to be illegal in STAR, FML

@TODO: Think about adding output as gziped fastq. 
fastq-dump --gzip --skip-technical  --readids --dumpbase --split-files --clip sra_filename
"""
rule fastqdump:
    input:
        sra      = SRA_FOLDER + SRA_FILE,
        metadata = METADATA_FOLDER + METADATA_FILE
    output:
        # Note: These are temp files, meaning these are delete when no rules remain that use these as input.
        fastq_1 = temp(FASTQDUMP_FOLDER + FASTQDUMP_FILE_1),
        fastq_2 = temp(FASTQDUMP_FOLDER + FASTQDUMP_FILE_2)
    run:
        # If no folder exists, create the folder.         
        shell("mkdir -p %s ;" % FASTQDUMP_FOLDER)
        
        # Get metadata to decide output method. 
        json_obj = json.load(open(input.metadata))
        layout = json_obj["LAYOUT"]
        
        # To handle both paired and single with the same rule create a fake second end.
        # I can't think of a more elegant solution. :(
        # Note: further in-elegance, fastq-dump uses the legacy argument when extracting as the newer  
        # does deletes some reads but not from both pairs if only one of the pairs is bad. 
        # This breaks STAR.
        if layout == "SINGLE":
            dummy_file_fix = " ; touch {output.fastq_2};"
            shell("/disk2/Resources/software/sratoolkit.2.10.5-centos_linux64/bin/fastq-dump.2.10.5 --split-files -O FASTQs {input.sra} " + dummy_file_fix )
        elif layout == "PAIRED":
            shell("/disk2/Resources/software/sratoolkit.2.10.5-centos_linux64/bin/fastq-dump.2.10.5 --split-files -O FASTQs {input.sra}")
        

"""
STAR_align runs guided alignments on the fastq files extracted from SRAs. 
It needs an index file for the guided alignment. So these must be built beforehand.
See the STAR documentation for details. 
"""
rule STAR_align:
    input:
        metadata = METADATA_FOLDER  + METADATA_FILE,
        first    = FASTQDUMP_FOLDER + FASTQDUMP_FILE_1,
        second   = FASTQDUMP_FOLDER + FASTQDUMP_FILE_2
    output:
       sam              = STAR_FOLDER + SAM,
       tx_bam           = temp(STAR_FOLDER + TX_BAM),
       chim             = STAR_FOLDER + CHIM,
       log_out_final    = STAR_FOLDER + LOG_OUT_FINAL,
       log_out          = STAR_FOLDER + LOG_OUT,
       log_progress_out = STAR_FOLDER + LOG_PROGRESS_OUT,
       out_tab          = STAR_FOLDER + OUT_TAB
    params:
       out_dir          = STAR_FOLDER + STAR_SAMPLE_DIR,
    run:
        SAMPLE_PREFIX = "sample_"
        # Make the STAR base folder and sample folder. 
        shell("mkdir -p %s ;" % STAR_FOLDER)
        shell("mkdir -p {params.out_dir}")
        
        # Get metadata about the current SRA. 
        json_obj = json.load(open(input.metadata))
        tax_id = json_obj["TAXON_ID"]
        layout = json_obj["LAYOUT"]
         
        # Build index path. 
        index_str = "%s/%s/%s/STAR" % (INDEX_BASE, VERSION, tax_id, )

        # There are more problems here with file ages, non-used files, etc. So touch all the output files. 
        # Append this to the send of main shell program so if the main program fails the rule will fail. 
        touch_files = """ ; 
            ls -l {output.sam};
            touch {output.tx_bam};
            touch {output.chim};
            touch {output.log_out_final}; 
            touch {output.log_out};  
            touch {output.log_progress_out}; 
            touch {output.out_tab}; """
        
        # Run STAR
        if layout == "SINGLE":
            star_str = """
            /disk2/Resources/software/STAR/bin/Linux_x86_64/STAR --runThreadN 5                            \
                 --runMode alignReads                      \
                 --outSAMtype BAM SortedByCoordinate       \
                 --genomeDir %s                            \
                 --outFileNamePrefix {params.out_dir}/%s   \
                 --chimSegmentMin 20                       \
                 --readFilesIn {input.first} ; ls -l {input.second}""" % (index_str, SAMPLE_PREFIX,)
                 
        elif layout == "PAIRED":
            star_str = """ 
            /disk2/Resources/software/STAR/bin/Linux_x86_64/STAR --runThreadN 5                            \
                 --runMode alignReads                      \
                 --outSAMtype BAM SortedByCoordinate       \
                 --genomeDir %s                            \
                 --outFileNamePrefix {params.out_dir}/%s   \
                 --chimSegmentMin 20                       \
                 --quantMode TranscriptomeSAM              \
                 --readFilesIn  {input.first} {input.second} """ % (index_str, SAMPLE_PREFIX,)
        else:
            print("ERROR", layout)
        
        shell(star_str + touch_files)
        
"""
In case of paired end data, Transcriptome output must be sorted by coordinate,
as it is a requirement for HTSeq-counts to have data sorted by reads or coordinates
"""
rule tx_sort:
    input:
        metadata         = METADATA_FOLDER  + METADATA_FILE,
        tx_bam           = STAR_FOLDER      + TX_BAM
    output:
        tx_bam_sorted    = STAR_FOLDER      + TX_BAM_SORTED
    run:

        # Get metadata about current SRA
        json_obj = json.load(open(input.metadata))
        layout = json_obj["LAYOUT"]

        # Run Samtools sort for paired end samples
        if layout == "SINGLE":
            sort_str = "touch {output.tx_bam_sorted} ;"

        elif layout == "PAIRED":
            sort_str = """
            /disk2/Resources/software/samtools-1.11/bin/samtools sort              \
            -n                           \
            -o {output.tx_bam_sorted}    \
            -O bam                       \
            {input.tx_bam} """
        else:
            print("ERROR", layout)

        shell(sort_str)

"""
makeHTSeqTables extracts counts from the STAR alignment for genes if a sigle end SRA is used, 
or genes and transcripts if a paired end SRA is used. 
"""
rule makeHTSeqTables:
    input:
        metadata         = METADATA_FOLDER + METADATA_FILE,
        sam              = STAR_FOLDER     + SAM,
        tx_bam_sorted    = STAR_FOLDER     + TX_BAM_SORTED
    output:
       genes_table       = HTSEQ_FOLDER    + GENES_TABLE,
       transcripts_table = HTSEQ_FOLDER    + TRANSCRIPT_TABLE
    run:
        # If no folder exists, create the folder. 
        shell( "mkdir -p %s " % HTSEQ_FOLDER  )

        json_obj = json.load(open(input.metadata))
        tax_id = json_obj["TAXON_ID"]
        layout = json_obj["LAYOUT"]
        
        # Build GTF file path. 
        # Note gtf files will need to be names in a regular fashion for this to work. 
        GTF_SOURCE = "gtf/"
        GTF_EXT = ".gtf"
        gtf_name = GTF_SOURCE + tax_id + GTF_EXT
        index_str = "%s/%s/%s/%s" % (INDEX_BASE, VERSION, tax_id, gtf_name)
        

        if layout == "SINGLE":
            htseq_gene_str = """
            /home/kasper/miniconda3/bin/htseq-count --quiet          \
                        --order    pos   \
                        --stranded no    \
                        --format   bam   \
                        --type     exon  \
                        --idattr gene_id \
                        {input.sam} %s > {output.genes_table} ; """ % index_str

            htseq_transcript_str = """touch {output.transcripts_table} ; """ 

            arguments = htseq_gene_str+" \n "+htseq_transcript_str

        elif layout == "PAIRED":
            htseq_gene_str = """
            /home/kasper/miniconda3/bin/htseq-count --quiet             \
                        --order    pos      \
                        --stranded no       \
                        --format   bam      \
                        --stranded no       \
                        --type     exon     \
                        --idattr   gene_id  \
                        {input.sam} %s > {output.genes_table} ; """ % index_str

            htseq_transcript_str = """
            /home/kasper/miniconda3/bin/htseq-count --quiet                  \
                        --order    pos           \
                        --stranded no            \
                        --format   bam           \
                        --stranded no            \
                        --type     exon          \
                        --idattr   transcript_id \
                        {input.tx_bam_sorted} %s > {output.transcripts_table} ; """ % index_str

            arguments = htseq_gene_str+" \n "+htseq_transcript_str
        else:
            print("ERROR", layout)
        
        shell(arguments)

"""
Cleanup
"""
rule cleanu:
    input:
        metadata         = METADATA_FOLDER + METADATA_FILE,
        tx_bam_sorted    = STAR_FOLDER     + TX_BAM_SORTED
    run:
        # If no folder exists, create the folder. 

        json_obj = json.load(open(input.metadata))
        layout = json_obj["LAYOUT"]

        cleanup_str = "echo `Nothing to clean`"
        if layout == "SINGLE":
            cleanup_str = "rm {input.tx_bam_sorted}"
        elif layout != "PAIRED":
            print("ERROR", layout)

        shell(cleanup_str)

        