#!/usr/bin/Rscript
# This program will process all tsv files in the directory passed. 
# These tsv files should be created from HTSeq-count output.
# Arg1 = Input folder path.
# Arg2 = Output file path.
suppressMessages(  library("DESeq", quietly = TRUE) )
suppressMessages(  library("DESeq2", quietly = TRUE) )


# sampleCondition <- sub("(.*transcripts.tsv)","\\1",sampleFiles)
# sampleTable <- data.frame(sampleName = sampleFiles, fileName = sampleFiles, condition = sampleCondition)
# ddsHTSeq <- DESeqDataSetFromHTSeqCount(sampleTable = sampleTable, directory = directory, design= ~ condition)

# Enable command line arguments.
args <- commandArgs(TRUE)

# Input path to input files. 
directory <-args[1]
print(args[1])

# Output file name and or path. 
output_file_name <- args[2]
print(output_file_name)


sampleFiles <- grep(".tsv", list.files(directory), value=TRUE)

sampleCondition <- sub("(.*.tsv)","\\1",sampleFiles)

sampleTable <- data.frame(sampleName = sampleFiles, fileName = sampleFiles, condition = sampleCondition)

ddsHTSeq <- DESeqDataSetFromHTSeqCount(sampleTable = sampleTable, directory = directory, design= ~ condition)

dds <- estimateSizeFactors(ddsHTSeq)

deseq_Ncounts <- counts(dds, normalized=TRUE)

write.table(file=output_file_name, x=deseq_Ncounts, quote=FALSE)


