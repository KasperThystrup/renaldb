# Programs and code used in the paper "*Logic programming to infer complex RNA expression patterns from RNA-seq data*"

This project can be broken into three major steps. Each step was largely preformed using Snakemake, so users looking
for more information about how each step was preformed should refer to these first. Additionally, one of the most important parts of the paper is the knowledge bases used to generate the specificty information. These can be found under Step 2's folder.

1. Step 1 - Assembling and extracting counts from the RNA-seq data used in the paper.
2. Step 2 - Normalizing the counts with between-sample and effective length and using this data to infer specificty.
3. Step 3 - Combining and formatting tables for inserting into RenalDB's relational database.# renaldb
