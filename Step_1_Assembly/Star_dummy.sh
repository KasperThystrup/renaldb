#!/bin/bash
OUTDIR=STAR_ASSEMBLIES/
GENOMEDIR=/disk2/Resources/seqDB/ensembl/release-100/9606/
MATE1=FASTQs/SRR8094770_1.fastq
MATE2=FASTQs/SRR8094770_2.fastq

/disk2/Resources/software/STAR/bin/Linux_x86_64/STAR --runThreadN 5                            \
                 --runMode alignReads                      \
                 --outSAMtype BAM SortedByCoordinate       \
                 --genomeDir $GENOMEDIR                            \
                 --outFileNamePrefix $OUTDIR   \
                 --chimSegmentMin 20                       \
                 --quantMode TranscriptomeSAM              \
                 --readFilesIn  $MATE1 $MATE2
