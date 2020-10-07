from xml.etree import ElementTree as ET
from urllib.request import urlopen
from urllib import error
from random import random
from time import sleep

import os
os.environ['http_proxy'] = ''
"""
    This class handles parsing of sra metadata given a list of SRA files.
    If the file is ran by itself an sra or wildcard describing SRAs can be passed
    and the parsed information will be printed in TSV format.
"""

UID_url_base = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=sra&term=%s"
sra_url_base = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=sra&id=%s"

# @TODO: Rewrite this to use this link so only one query is nedded to parse the info.
# @TODO: Clean this up and add comments.
# sra_direct_base = "http://www.ncbi.nlm.nih.gov/sra/?term=%s&report=FullXml&format=text"
# http://www.ncbi.nlm.nih.gov/sra/?term=SRR2146358&report=FullXml&format=text
# https://www.biostars.org/p/5314/


def SRAXMLToJSON(sra_id):
    NA_str = 'NA'
    attribute_set = set()
    sra_list = []
    standard_elements = {
        "EXPERIMENT_alias": "",
        "EXPERIMENT_accession": "",
        "SAMPLE_DESCRIPTOR_accession": "",
        "STUDY_alias": "",
        "STUDY_accession": "",
        "RUN_accession": "",
        "BioProject": "",
        "BioSample": "",
        "TAXON_ID": "",
        "INSTRUMENT_MODEL": "",
        "LAYOUT": "",
        "STUDY_TITLE": "",
        "LIBRARY_SELECTION": "",
        "LIBRARY_STRATEGY": "",
        "sample_attribs": {},
        "ftp_link": ""
    }

    sleep(0.1+random()*1)
    add_attributes = False
    tmp_tag = None
    attribute_dict = dict()
    sleep(0.1+random()*1)    
    sra_id = sra_id.split('.')[0].split('_')[0]
    print(UID_url_base % sra_id)
    search_xml = urlopen(UID_url_base % sra_id)
    
    UID_list = []
    for event, elem in ET.iterparse(search_xml, events=("start", "end")):
        if elem.tag == "Id" and event == "end":
            UID_list.append(elem.text)
    assert len(UID_list) == 1
    UID = UID_list[0]
    # http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=sra&term=SRX015714
    # http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=sra&id=16175
    # UID = convertSRAidtoUID(sra_id)
    # To prevent our IP from being blocked. 
    sleep(0.1+random()*1)
    xml = urlopen(sra_url_base % UID)

    for event, elem in ET.iterparse(xml, events=("start", "end")):
        # print event, elem, elem.tag, elem.__dict__

        if elem.tag == "SAMPLE_ATTRIBUTES":
            if event == "start": add_attributes = True
            else: add_attributes = False

        # LIBRARY_LAYOUT
        if elem.tag == "SINGLE":
            standard_elements["LAYOUT"] = 'SINGLE'
        if elem.tag == "PAIRED":
            standard_elements["LAYOUT"] = 'PAIRED'

        if event == "start":
            #<EXPERIMENT alias="GSM1281777" accession="SRX388276" center_name="GEO">
            if (elem.tag == "EXPERIMENT" and 'alias' in elem.attrib):
                standard_elements["EXPERIMENT_alias"] = elem.attrib['alias'].split(':')[0]
            if (elem.tag == "EXPERIMENT" and 'accession' in elem.attrib ):
                standard_elements["EXPERIMENT_accession"] = elem.attrib['accession']
            #<SAMPLE_DESCRIPTOR accession="SRS512164">
            if (elem.tag == "SAMPLE_DESCRIPTOR" and 'accession' in elem.attrib ):
                standard_elements["SAMPLE_DESCRIPTOR_accession"] = elem.attrib['accession']
            #<STUDY center_name="GEO" alias="GSE53080" accession="SRP033566">
            if (elem.tag == "STUDY" and 'alias' in elem.attrib ):
                standard_elements["STUDY_alias"] = elem.attrib['alias'].split(':')[0]
            if (elem.tag == "STUDY" and 'accession' in elem.attrib ):
                standard_elements["STUDY_accession"] = elem.attrib['accession']
            #<SUBMISSION accession="SRA115414">
            #if (elem.tag == "SUBMISSION" and 'accession' in elem.attrib ):
            #    SUBMISSION_accession = elem.attrib['alias']
            #<RUN alias="GSM1281777_r1" accession="SRR1044485"  >
            if elem.tag == "RUN" and 'accession' in elem.attrib:
                #!!!! This will be incorrect if multiple samples are avalible per SRA entry. Ex: http://www.ncbi.nlm.nih.gov/sra/SRR786474/
                #standard_elements["RUN_accession"] = elem.attrib['accession']
                standard_elements["RUN_accession"] = sra_id
        elif event == "end":
            #<EXTERNAL_ID namespace="BioProject">PRJNA230811</EXTERNAL_ID>
            if (elem.tag == "EXTERNAL_ID" and 'namespace' in elem.attrib and elem.attrib['namespace'] == "BioProject"):
                standard_elements["BioProject"] = elem.text
            #<EXTERNAL_ID namespace="BioSample">SAMN02437825</EXTERNAL_ID>
            if (elem.tag == "EXTERNAL_ID" and 'namespace' in elem.attrib and elem.attrib['namespace'] == "BioSample"):
                standard_elements["BioSample"] = elem.text
            #<TAXON_ID>9606</TAXON_ID>
            if elem.tag == "INSTRUMENT_MODEL":
                standard_elements["INSTRUMENT_MODEL"] = elem.text
            #<TAXON_ID>9606</TAXON_ID>
            if elem.tag == "LIBRARY_STRATEGY":
                standard_elements["LIBRARY_STRATEGY"] = elem.text
            if elem.tag == "LIBRARY_SELECTION":
                standard_elements["LIBRARY_SELECTION"] = elem.text
            #<TAXON_ID>9606</TAXON_ID>
            if elem.tag == "TAXON_ID":
                standard_elements["TAXON_ID"] = elem.text
            #STUDY_TITLE
            if elem.tag == "STUDY_TITLE":
                standard_elements["STUDY_TITLE"] = elem.text

            if add_attributes and elem.tag == "TAG":
                tmp_tag = elem.text
                standard_elements["sample_attribs"].update({tmp_tag:""})
            if add_attributes and elem.tag == "VALUE":
                if not tmp_tag in attribute_dict:
                    standard_elements["sample_attribs"][tmp_tag] = elem.text
                else:
                    print( "warning")
    
    standard_elements["ftp_link"] = "/".join(
        [
            "ftp://ftp-trace.ncbi.nlm.nih.gov/sra/sra-instant/reads/ByExp/sra",
            standard_elements['EXPERIMENT_accession'][:3], 
            standard_elements['EXPERIMENT_accession'][:6],
            standard_elements['EXPERIMENT_accession'],               
            # A quick and dirty fix for multi-sample SRAs. 
            sra_id,
            sra_id+".sra"
            # 
            #standard_elements['RUN_accession'],
            #standard_elements['RUN_accession']+".sra"
        ]
    )

    return standard_elements


if __name__ == '__main__':
    
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(type=str, help='A file of SRA IDs', dest='input_sras', default=False)
    args = parser.parse_args()

    if args.input_sras:
        
        import json
        from time import time
        sra_id_list = []
        cnt = 0
        for sra_path in open(args.input_sras):
            try:
                sra_json_tmp = SRAXMLToJSON(sra_path.strip())
                json_txt = json.dumps(sra_json_tmp, sort_keys=True, indent=4, separators=(',', ': '))
                f_obj = open(sra_path.strip()+".json",'w')
                f_obj.write(json_txt)
                f_obj.close()        
                status = "SUCESS"
            except error.HTTPError:
                status = "FAILURE"
            print( sra_path.strip(), status, time(), cnt ) 
            cnt+=1
    else:
        print(SRAXMLToJSON("SRR2146358"))


