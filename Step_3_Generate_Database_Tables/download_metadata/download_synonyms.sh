mysql --host=ensembldb.ensembl.org --port=3306 --user=anonymous homo_sapiens_core_83_38  < get_synonyms.sql > homo_sapiens_core_83_38.synonyms.tsv
mysql --host=ensembldb.ensembl.org --port=3306 --user=anonymous mus_musculus_core_83_38  < get_synonyms.sql > mus_musculus_core_83_38.synonyms.tsv
mysql --host=ensembldb.ensembl.org --port=3306 --user=anonymous danio_rerio_core_83_10  < get_synonyms.sql > danio_rerio_core_83_10.synonyms.tsv
