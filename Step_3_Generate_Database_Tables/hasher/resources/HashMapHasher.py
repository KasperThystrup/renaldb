from hashlib import sha1, md5
import base64


def UGAHash(seq_type, assembly, chromosome, strand, start_end_list):
    #http://crypto.stackexchange.com/questions/231/change-in-probability-of-collision-when-removing-digits-from-md5-hexadecimal-has
    ugahash_tag = "U"
    field_separator = "_"
    bound_list = []
    #print(seq_type, assembly, chromosome, strand, start_end_list)
    chromosome = chromosome.strip("chr")
    prev_start, prev_stop = None, None
    for start, stop in start_end_list:
        tmp_start, tmp_stop = sorted([int(start), int(stop)])
        assert ((prev_start is None or prev_start < tmp_start) ), start_end_list  #and (prev_stop is None or prev_stop < tmp_stop)
        bound_list.append(str(tmp_start)+"-"+str(tmp_stop))
        prev_start, prev_stop = tmp_start, tmp_stop
    bounds = ":".join(bound_list)
    md5_digest = md5(chromosome+"_"+strand+"_"+bounds).digest()
    base64_endoced_md5_digest = base64.urlsafe_b64encode(md5_digest)[:-2]
    return field_separator.join((ugahash_tag+seq_type, assembly+base64_endoced_md5_digest))


if __name__ == '__main__':
    #Parse bed to database tsv.
    import sys

    source = sys.argv[2]
    tax_id = sys.argv[3]
    assembly = sys.argv[4]
    seq_type = "G"

    for line in open(sys.argv[1]):
        spln = line.split()

        chromosome = spln[0].strip("chr")
        start = spln[1]
        end = spln[2]
        original_id = spln[3]

        strand = "."
        if len(spln) > 4:
            strand = spln[5]

        id = UGAHash(seq_type, tax_id, assembly, chromosome, ((start, end), ), strand)

        print("\t".join((id, original_id, source, tax_id, assembly, chromosome, start, end, strand)))

