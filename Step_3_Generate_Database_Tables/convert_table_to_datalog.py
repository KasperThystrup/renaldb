""" This is a helper function which converts a table into Datalog facts given a file containing Datalog rules.
The table must have titles for all columns, and the Datalog rules must match.

Column names must be unique.
For each row, a set of facts will be created from the available rules, using the

"""
import argparse

parser = argparse.ArgumentParser()

parser.add_argument('--table', dest='table', required=True,
                    help="A tab delimited table, each column must have a title.")

parser.add_argument('--rules', dest='rules', required=True,
                    help="A set of Datalog/Prolog rules with one rule per line.")

args = parser.parse_args()


# Make column name -> index dict.

table_file_obj = open(args.table)

# Build a dictionary using title names as keys and column positions as values.
titles = table_file_obj.readline().strip("\n").split("\t")
col_number = 0
col_name_number_dict = {}

for title in titles:
    # Non-Unique col names will cause errors, and original number
    assert title not in col_name_number_dict
    col_name_number_dict[title] = col_number
    col_number += 1

# Parse rules
rule_list = []
for line in open(args.rules):
    # Rules should be formatted like rule(Varible1, Varible2, ...)

    #print(line.strip(")"))

    rule_name, variables = line.split("(")

    #print(variables.rstrip(")"))

    variables = [x.strip() for x in variables.split(")")[0].split(",")]

    for x in variables:

        assert x in col_name_number_dict, x

    rule_list.append([rule_name, variables])


for line in table_file_obj:

    if line.strip() != "":
        split_line = line.strip().split("\t")

        for rule in rule_list:
            rule_name = rule[0]
            rule_variables = rule[1]
            # Build atom list in same order as parsed.
            atom_list = []
            contains_none = False
            for rule_variable in rule_variables:
                col_index = col_name_number_dict[rule_variable]
                col_value = split_line[col_index]

                # Do not print columns with None values.
                # As these are not useful information.
                if col_value == "None":
                    contains_none = True

                atom_list.append('"'+col_value+'"')

            # For facts in pyDatalog print starting with a plux sign.
            if not contains_none:
                print("+ "+rule_name+'('+", ".join(atom_list)+')')

        # Print a new line between rows for readability.
        print('')





