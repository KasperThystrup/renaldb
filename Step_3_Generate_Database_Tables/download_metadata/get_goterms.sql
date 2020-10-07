SELECT stable_id, dbprimary_acc, linkage_type, xref.description FROM ontology_xref 
JOIN xref ON ontology_xref.source_xref_id = xref.xref_id 
JOIN object_xref ON ontology_xref.source_xref_id = object_xref.object_xref_id
JOIN gene ON gene.gene_id = object_xref.ensembl_id
JOIN external_db ON external_db.external_db_id = xref.external_db_id
WHERE external_db.db_name = 'GO';
