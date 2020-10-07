SELECT stable_id, description FROM gene
UNION
SELECT stable_id, description FROM transcript;
