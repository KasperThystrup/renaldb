SELECT DISTINCT stable_id, "name", seq_name FROM (
    SELECT stable_id, value as seq_name FROM gene 
    JOIN gene_attrib ON gene.gene_id = gene_attrib.gene_id 
    JOIN attrib_type ON attrib_type.attrib_type_id = gene_attrib.attrib_type_id WHERE 
    attrib_type.code = "name" 
    UNION
    SELECT stable_id, value as seq_name FROM transcript 
    JOIN transcript_attrib ON transcript.transcript_id = transcript_attrib.transcript_id 
    JOIN attrib_type ON attrib_type.attrib_type_id = transcript_attrib.attrib_type_id WHERE 
    attrib_type.code = "name" 
)z;
