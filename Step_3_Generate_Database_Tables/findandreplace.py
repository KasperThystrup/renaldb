"""
This is a simple script to replace accessions with UGAs
It needs a tsv  mapping file with the original id in the first column and the UGA in the second. 
Any tsv file can be used for the second.
It adds a  
"""
import sys


dict_file = sys.argv[1]

convert_file = sys.argv[2]

mapping_dict = {}

for line in open(dict_file): 
    spln = line.strip().split("\t")
    if len(spln) > 0:
        key, val = spln 
        #print(key, val)
        mapping_dict[key] = val


for line in open(convert_file):
    spln = line.strip().split("\t")
    print("null", end="\t")
    for el in spln: 

        if el in mapping_dict:
            out = mapping_dict[el]    
        else:
            out = el

        print(out, end="\t")

    print("")



