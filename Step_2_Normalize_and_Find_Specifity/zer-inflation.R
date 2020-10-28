library(zzinflationR)

setwd("~/renaldb/Step_1_Assembly")

count_files <- c(
  list.files(path = "HTSeqTables", pattern = "genes\\.tsv", full.names = TRUE)
)
counts <- zzinflationR::importCounts(count_files)

trimmed <- zzinflationR::trimCounts(data = counts, threshold = 99)

path = "../Step_2_Normalize_and_Find_Specifity/HTSeqCounts_Passed_Cutoff/genes_9606.tsv"

readr::write_tsv(x = tibble::rownames_to_column(trimmed, "ID"), path, na = "0")



count_files <- c(
  list.files(path = "HTSeqTables", pattern = "transcripts\\.tsv", full.names = TRUE)
)
counts <- zzinflationR::importCounts(count_files)

trimmed <- zzinflationR::trimCounts(data = counts, threshold = 98)

path = "../Step_2_Normalize_and_Find_Specifity/HTSeqCounts_Passed_Cutoff/transcripts_9606.tsv"

readr::write_tsv(tibble::rownames_to_column(trimmed, "ID"), path, na = "0")

