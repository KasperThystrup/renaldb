# Step 2 Normalize Expression Values and Find Specifity

The Snakemake program in this folder deals with normalizing counts between samples, normalizing individual sequences by length, using these values to calculate sequence specficity, and finally preparing these as
tables to insert into a relational database.


There are some important programs relating to the paper in this section.
These are:
1. The Datalog knowledge bases used in RenalDB
	1. kidney_anatomy.dl - Contains facts about human, mouse, and Zebrafish anatomy.
	2. renaldb_experiments_knowledge.dl - Contains facts about experiment sources and metadata.
	3. renaldb_logic_structures.dl - Contains rules defining various kinds of specificity.
2. generate_localization_relations.py - This program generates a table of specifity relations.



