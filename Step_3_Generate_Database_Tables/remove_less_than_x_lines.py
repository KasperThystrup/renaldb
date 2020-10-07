import sys

line_numb_cutoff = 4

for line in open(sys.argv[1]): 
    spln = line.split("\t")

    if len(spln) > 4:
         print(line, end="")

