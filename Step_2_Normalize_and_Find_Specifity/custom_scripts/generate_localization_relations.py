""" This program takes: 
1. Anatomy knowledge base
2. Experimenet metadata knowledge base, 
3. Logical relationship rules knowledge base 
4. A set of expression relations, as a tsv file sorted by sequence id. 

It outputs relationships for input into a database.

At the moment it outputs:
1. Expressed in
2. Enriched in
3. Specific to


@TODO: Ideas for other output types. 
Possibly Specific to
Possibly Enriched in 
physical localization
temporal localization

"""
import argparse
from pyDatalog import pyDatalog as pd


def generatelocalizationrelations(seq_id, attribute_val_set):
    """Given a sequence ID and an attribute value set of facts. Find the
    expression specificity properties of the given sequence and print them as tab separated values.

    expression("seq_id", "experiment", exp_val)

    """
    #Load functors
    attrib_functors = "+ "+"\n+ ".join(list(attribute_val_set))
    # print attrib_functors
    pd.load(attrib_functors)

    # Test for expression
    expressed_set = pd.ask('''expressedin("%s", Source)''' % seq_id)
    if expressed_set:
        for component_el in [x[0] for x in expressed_set.answers]:
            print("\t".join([seq_id, "expressed", component_el]))

    # Test for enrichment
    enriched_set = pd.ask('''enrichedin("%s", Source)''' % seq_id)
    if enriched_set:
        for component_el in [x[0] for x in enriched_set.answers]:
            print("\t".join([seq_id, "enriched", component_el]))

    # Test for specificity
    # This is more complicated than expression or enrichment and is not perfect at the moment.
    # For example, in the future inferring potential specificity would be interesting.
    # However, we can only move to higher tissues in this version.

    # First we need to find the expression of the sequence and it's parents.
    experiment_set = pd.ask('''expression("%s", Experiment, ExpVal)''' % seq_id)
    # Ensure experiment exists.
    if experiment_set:

        specific_set = None
        # For each experiment expressing the given sequence
        for experiment_id in [x[0] for x in experiment_set.answers]:

            # Find self and parents sources.
            # "Kidney Cortex"   -> ("Kidney",), ("Kidney Cortex",)
            #  "Kidney Medulla" ->  ("Kidney",), ("Kidney Medulla",)
            tmp_specific_obj = pd.ask('''sourceandparents("%s", Source)''' % (experiment_id,))

            # Check to ensure a source exists.
            if tmp_specific_obj:

                # Get a set of the source and parent tissues.

                tmp_specific_set = set(x[0] for x in tmp_specific_obj.answers)

                if specific_set is None:
                    # Add the first sources to the set.
                    specific_set = tmp_specific_set
                else:
                    # Intersect the contained sources and the new sources.
                    # This was common parents are preserved.
                    # Giving the highest specificity available, or an empty set.
                    # set(("Kidney",), ("Kidney Cortex",)) & set(("Kidney",), ("Kidney Medulla",)) -> set("Kidney")
                    specific_set = specific_set & tmp_specific_set
            else:
                assert False, "Error, should always have expression."

        for component_el in specific_set:
            print("\t".join([seq_id, "specific", component_el]))

    # Remove facts.
    attrib_functors = "- "+"\n- ".join(list(attribute_val_set))
    pd.load(attrib_functors)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument(
        '-a', '--anatomy_facts',
        dest='anatomy_facts',
        required=True,
        help="A file containing anatomy information in the form of a pyDatalog facts."
    )

    parser.add_argument(
        '-s', '--experiment_facts',
        dest='experiment_facts',
        required=True,
        help="A file containing information of the experiments source and other metdata in the form of pyDatalog facts."
    )

    parser.add_argument(
        "-r", "--expression_rules",
        dest="expression_rules",
        required=True,
        help="Datalog relations describing expression relationships in the form of pyDatalog rules."
    )

    parser.add_argument(
        "-e", "--expression_instances",
        dest='expression_instances',
        required=True,
        help="A TSV file containing sequence IDs, experiment IDs, and expression values, SORTED BY SEQUENCE ID."
    )

    args = parser.parse_args()

    # Load anatomy facts.
    anatomy_facts_txt = open(args.anatomy_facts).read()
    pd.load(anatomy_facts_txt)

    # Load experiment source and metadata facts.
    experiment_facts_txt = open(args.experiment_facts).read()
    pd.load(experiment_facts_txt)

    # Load expression rules.
    expression_rules_txt = open(args.expression_rules).read()
    pd.load(expression_rules_txt)

    # This is used as an error checking step.
    # If the sequence IDs are not in order this will cause an assertion error.
    previous_sequence_set = set()

    # This stores facts to be passed to the specificity calculating function.
    expression_fact_set = set()

    # This id stores the previously seen sequence ids.
    previous_id = None

    for line in open(args.expression_instances):

        spln = line.split()
        seq_id, experiment, exp_val = spln

        # If the current ID is different than the previous id
        if previous_id != seq_id and previous_id is not None:

            # This will fail if the same sequence ID is seen twice i.e. with other sequences
            # between them.
            assert previous_id not in previous_sequence_set
            previous_sequence_set.add(previous_id)

            # Generate the specificity relations, this prints to stdout
            # So nothing is returned by the function.
            generatelocalizationrelations(previous_id, expression_fact_set)

            # Clear the facts set after use.
            expression_fact_set = set()

        # Update the last seen id.
        previous_id = seq_id
        # Generate a fact in text form. Wait to add + or - since they will be deleted after use.
        expression_fact = """expression("%s", "%s", %s)""" % (seq_id, experiment, exp_val,)
        # Store a set of facts.
        expression_fact_set.add(expression_fact)

    # Handle the last sequence.
    generatelocalizationrelations(seq_id, expression_fact_set)



