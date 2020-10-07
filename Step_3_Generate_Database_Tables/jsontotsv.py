import sys
import argparse
import json

#sys.stdout.buffer.write(chr(9986).encode('utf8'))

'''
Add this to start if having encoding errors
PYTHONIOENCODING=utf-8

'''


parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)

parser.add_argument('jsonfiles', 
    metavar='jsonfiles', 
    type=str, 
    nargs='+',
    help='a regex of json files')

args = parser.parse_args()

sample_attribs_set = set()

for file_name in args.jsonfiles:

    json_obj = json.load(open(file_name))
    sample_attribs = json_obj['sample_attribs']
    sample_attribs_set.update( set(sample_attribs.keys()) )

sorted_attribs = list(sorted(sample_attribs_set))

set_titles = ["STUDY_GEO_ID", "EXPERIMENT_alias", "SRA_ID", "TAXID", 
"INSTRUMENT_MODEL", "LAYOUT"] + sorted_attribs

print("\t".join(set_titles))

for file_name in args.jsonfiles:

    json_obj = json.load(open(file_name))
    STUDY_GEO_ID = json_obj["STUDY_alias"]
    SRA_ID = json_obj["RUN_accession"]
    TAXID = json_obj["TAXON_ID"]
    INSTRUMENT_MODEL = json_obj["INSTRUMENT_MODEL"]
    LAYOUT = json_obj["LAYOUT"]
    EXPERIMENT_alias = json_obj["EXPERIMENT_alias"]

    out_attrib_values = []
    for attrib in sorted_attribs:
        out_val = "None"
        if attrib in json_obj['sample_attribs']:
            out_val = json_obj['sample_attribs'][attrib]
        out_attrib_values.append(out_val)

    out_total = [STUDY_GEO_ID, EXPERIMENT_alias, SRA_ID, TAXID, 
    INSTRUMENT_MODEL, LAYOUT] + out_attrib_values

    print("\t".join(out_total))
    
    '''
    try:
        print("\t".join(out_total))
    except:
        print("\t".join(out_total).decode()) 
    '''
