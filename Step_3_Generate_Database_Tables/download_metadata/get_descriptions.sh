mysql --host=ensembldb.ensembl.org --port=3306 --user=anonymous homo_sapiens_core_83_38  < get_seq_descriptions.sql > homo_sapiens_core_83_38.descriptions.tsv
mysql --host=ensembldb.ensembl.org --port=3306 --user=anonymous mus_musculus_core_83_38  < get_seq_descriptions.sql > mus_musculus_core_83_38.descriptions.tsv
mysql --host=ensembldb.ensembl.org --port=3306 --user=anonymous danio_rerio_core_83_10   < get_seq_descriptions.sql > danio_rerio_core_83_10.descriptions.tsv
