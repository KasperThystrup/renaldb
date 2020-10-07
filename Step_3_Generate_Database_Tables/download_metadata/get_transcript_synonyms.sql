SELECT DISTINCT stable_id, seq_name FROM (
    SELECT stable_id, synonym as seq_name FROM transcript 
    JOIN external_synonym ON transcript.display_xref_id = external_synonym.xref_id
    UNION
    SELECT stable_id, value as seq_name FROM transcript 
    JOIN transcript_attrib ON transcript.transcript_id = transcript_attrib.transcript_id 
    JOIN attrib_type ON attrib_type.attrib_type_id = transcript_attrib.attrib_type_id WHERE 
    (attrib_type.code = "name" or attrib_type.code = "synonym")
)z;
