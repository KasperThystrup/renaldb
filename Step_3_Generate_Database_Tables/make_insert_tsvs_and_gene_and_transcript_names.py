__author__ = 'tyler'
import json
import re
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--json_file', dest='json_file', required=True, help="")
parser.add_argument('--source', dest='source', help="")
parser.add_argument('--source_version', dest='source_version', help="")
parser.add_argument('--source_base_url', dest='source_base_url', help="")
parser.add_argument('--assembly', dest='assembly', help="")
parser.add_argument('--tax_id', dest='tax_id', help="")
#parser.add_argument('--exon_url', dest='exon_url', help="")
#parser.add_argument('--gene_url', dest='gene_url', help="")
#parser.add_argument('--transcript_url', dest='transcript_url', help="")
args = parser.parse_args()
#from lncRNACoordinateMapper.models import SequenceSet, Genes, Transcripts, Exons, TranscriptExonRelations
from .hasher.resources import HashMapHasher
#from django.utils.safestring import mark_safe
#Register your models here.

def naturallysorted(L, reverse=False):
    """ Similar functionality to sorted() except it does a natural text sort
    which is what humans expect when they see a filename list. """
    convert = lambda text: ('', int(text)) if text.isdigit() else (text, 0)
    alphanum = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    return sorted(L, key=alphanum, reverse=reverse)

json_obj = json.load(open(args.json_file))
gene_dict = json_obj['gene']

print("\t".join([args.source+"_"+args.source_version, args.source,
                 args.source_version,
                 args.tax_id, args.assembly, args.source_base_url]))


genes_set = set()
transcripts_set = set()
exons_set = set()
transcript_exon_relations_set = set()
sequenceset_list = []
sequence_table = []
parentchildseqrelations_list = []
sequencesetsequencerelation = []
seq_names = []
seq_biotypes = []

#source_version_id = models.ForeignKey(SequenceSet)
#hash_id = models.ForeignKey(Sequence)
#original_id = models.CharField(max_length=80)

for gene_id in gene_dict:

    gene_obj = gene_dict[gene_id]


    g_start, g_stop = sorted(
        [int(gene_obj['start']), int(gene_obj['stop'])]
    )

    gene_hashed_ac = HashMapHasher.UGAHash(
        'G', args.assembly, gene_obj['chromosome'].strip("chr"), gene_obj['strand'], ((g_start, g_stop),)
    )

    sequenceset_list.append(
        "\t".join(
            [
                gene_hashed_ac,
                args.assembly,
                gene_obj['chromosome'].strip("chr"),
                gene_obj['strand'],
                gene_obj['start'],
                gene_obj['stop'],
                "gene",
                args.tax_id
            ]
        )
    )

    sequencesetsequencerelation.append("\t".join((
        'null', gene_id, gene_hashed_ac, args.source+"_"+args.source_version
    )))
    
    seq_names.append( "\t".join( [  'null', 'name', gene_hashed_ac, gene_obj['gene_name'] ] )  )
    
    if gene_obj['gene_biotype'] != "":
        g_biotype = gene_obj['gene_biotype']    
    else:
        g_biotype = "Unknown"

    seq_biotypes.append( "\t".join( ['null', 'biotype', g_biotype, gene_hashed_ac ] ) )

    for transcript_id in gene_obj['transcript']:
        #print(transcript_id)
        t_obj = gene_obj['transcript'][transcript_id]

        exon_bounds_list = []
        for exon_id in t_obj['exon']:
            exon_obj = t_obj['exon'][exon_id]

            t_start, t_stop = sorted(
                [int(exon_obj['start']), int(exon_obj['stop'])]
            )

            exon_bounds_list.append(
                (t_start, t_stop)
            )

        
        try:
            transcript_hashed_ac = HashMapHasher.UGAHash(
                'T', args.assembly, gene_obj['chromosome'].strip("chr"), gene_obj['strand'], sorted(exon_bounds_list)
                #'T', args.assembly, gene_obj['chromosome'].strip("chr"), gene_obj['strand'], sorted(list(set(exon_bounds_list)))
            )
        except:
            print(transcript_id)

        sequenceset_list.append(
            "\t".join(
                [
                    transcript_hashed_ac,
                    args.assembly,
                    gene_obj['chromosome'].strip("chr"),
                    gene_obj['strand'],
                    t_obj['start'],
                    t_obj['stop'],
                    'transcript',
                    args.tax_id
                ]
            )
        )

        sequencesetsequencerelation.append(
            "\t".join(("null", transcript_id, transcript_hashed_ac, args.source+"_"+args.source_version ))
        )

        parentchildseqrelations_list.append(

            "\t".join((
                'null', 'gene', 'transcript', "0", transcript_hashed_ac, gene_hashed_ac
            ))
        )

        seq_names.append( "\t".join( [ 'null', 'name', transcript_hashed_ac, t_obj['transcript_name']  ] ) )
        
        t_biotype = "Unknown"
        if t_obj['transcript_biotype'] != "":
            t_biotype = t_obj['transcript_biotype']    
         
        seq_biotypes.append( "\t".join( [ 'null', 'biotype', t_biotype, transcript_hashed_ac  ] ) )


        for exon_id in naturallysorted(t_obj['exon']):

            exon_obj = t_obj['exon'][exon_id]


            e_start, e_stop = sorted(
                [int(exon_obj['start']), int(exon_obj['stop'])]
            )

            exon_hashed_ac = HashMapHasher.UGAHash(
                'E', args.assembly, gene_obj['chromosome'].strip("chr"),
                gene_obj['strand'], ((e_start, e_stop),)
            )

            sequenceset_list.append(
                "\t".join(
                    [
                        exon_hashed_ac,
                        args.assembly,
                        gene_obj['chromosome'].strip("chr"),
                        gene_obj['strand'],
                        exon_obj['start'],
                        exon_obj['stop'],
                        'exon',
                args.tax_id
                    ]
                )
            )

            sequencesetsequencerelation.append(
                "\t".join((
                   'null', exon_id, exon_hashed_ac, args.source+"_"+args.source_version
                )))

            parentchildseqrelations_list.append(
                "\t".join((
                    'null', 'gene',       'exon', "0", exon_hashed_ac, gene_hashed_ac,
                ))
            )

            parentchildseqrelations_list.append(
                "\t".join((
                    'null', 'transcript', 'exon', exon_id, exon_hashed_ac, transcript_hashed_ac

                ))
            )


seq_biotypes
out_f = open(args.source+"_"+args.source_version+"_"+args.tax_id+"_biotypes.txt", 'w')
out_f.write("\n".join(seq_biotypes))
out_f.close()

out_f = open(args.source+"_"+args.source_version+"_"+args.tax_id+"_names.txt", 'w')
out_f.write("\n".join(seq_names))
out_f.close()

out_f = open(args.source+"_"+args.source_version+"_"+args.tax_id+"_sequences.txt", 'w')
out_f.write("\n".join(sequenceset_list))
out_f.close()

out_f = open(args.source+"_"+args.source_version+"_"+args.tax_id+"_sequence_set.txt", 'w')
out_f.write("\n".join(sequencesetsequencerelation))
out_f.close()

out_f = open(args.source+"_"+args.source_version+"_"+args.tax_id+"_parent_child.txt", 'w')
out_f.write("\n".join(parentchildseqrelations_list))
out_f.close()

#out_f.write(print "\t".join(, args.source, args.source_version,
#                args.tax_id, args.assembly, args.source_base_url))




