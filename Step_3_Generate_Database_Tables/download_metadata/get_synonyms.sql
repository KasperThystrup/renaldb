SELECT DISTINCT stable_id, "synonym", seq_name FROM (
    SELECT stable_id, synonym as seq_name FROM gene 
    JOIN external_synonym ON gene.display_xref_id = external_synonym.xref_id
    UNION
    SELECT stable_id, value as seq_name FROM gene 
    JOIN gene_attrib ON gene.gene_id = gene_attrib.gene_id 
    JOIN attrib_type ON attrib_type.attrib_type_id = gene_attrib.attrib_type_id WHERE 
    (attrib_type.code = "synonym")
    UNION
    SELECT stable_id, synonym as seq_name FROM transcript 
    JOIN external_synonym ON transcript.display_xref_id = external_synonym.xref_id
    UNION
    SELECT stable_id, value as seq_name FROM transcript 
    JOIN transcript_attrib ON transcript.transcript_id = transcript_attrib.transcript_id 
    JOIN attrib_type ON attrib_type.attrib_type_id = transcript_attrib.attrib_type_id WHERE 
    (attrib_type.code = "synonym")
)z;

