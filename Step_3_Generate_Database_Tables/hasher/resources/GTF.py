import re


class CuffcompareGTF:

    def __init__(self, gtf_file_name):
        self.gene_id_dict = {}
        self.transcript_id_dict = {}
        self.exon_dict = {}

        for line in open(gtf_file_name):
            self.addline(line)

    def genes(self):
        for el in self.gene_id_dict:
            yield self.gene_id_dict[el]

    def transcripts(self):
        for el in self.transcript_id_dict:
            yield self.gene_id_dict[el]

    def exons(self):
        for el in self.exon_list:
            yield el

    class Exon:
        def __init__(self, tsv_line):
            spln = tsv_line.strip().split("\t")
            self.chromosome = spln[0]
            self.start = spln[3]
            self.end = spln[4]
            self.score = spln[5]
            self.strand = spln[6]
            self.frame = spln[7]
            self.exon_number = re.findall(r'exon_number "(.*?)";', tsv_line)[0] # exon_number "1";
            #self.exon_id = re.findall(r'exon_id "(.*?)";', tsv_line)[0]
            #self.exon_version = re.findall(r'exon_version "(.*?)";', tsv_line)[0]

    class Gene:

        def transcripts(self):
            for el in self.transcripts_dict:
                yield self.transcripts_dict[el]

        #def add_exon(self, exon_name, exon_obj):
        #    if not exon_name in self.exons_dict:
        #        self.exons_dict.update({exon_name: exon_obj})

        def add_exon(self, tmp_exon_obj):

            #tmp_exon_obj = self.Exon(exon_line)

            self.exons_dict.update({str(tmp_exon_obj.start)+"-"+str(tmp_exon_obj.end): tmp_exon_obj})

            if self.start is None or self.start == "" or int(tmp_exon_obj.start) < int(self.start):
                self.start = tmp_exon_obj.start
            if self.start is None or self.start == "" or int(tmp_exon_obj.end) < int(self.start):
                self.start = tmp_exon_obj.end

            if self.end is None or self.end == "" or int(tmp_exon_obj.start) > int(self.start):
                self.end = tmp_exon_obj.start
            if self.end is None or self.end == "" or int(tmp_exon_obj.end) > int(self.end):
                self.end = tmp_exon_obj.end


        def __init__(self, tsv_line=None):
            self.gene_info_set = False
            self.chromosome = ""
            self.source = ""
            self.start = ""
            self.end = ""
            self.score = ""
            self.strand = ""
            self.frame = ""
            self.gene_version = ""
            self.gene_name = ""
            self.gene_source = ""
            self.gene_biotype = ""
            self.gene_id = ""       # gene_id "XLOC_000001";
            self.transcript_id = "" # transcript_id "TCONS_00000001";
            self.frac = ""
            self.conf_lo = ""
            self.conf_hi = ""
            self.class_code = ""
            self.cov = []
            self.gene_name = ""   #gene_name "Gm16088";
            self.oId = ""         #oId "ENSMUST00000160944";
            self.exons_dict = {}
            self.exon_list = []
            self.class_code = ""  #class_code "=";
            self.tss_id = ""      #tss_id "TSS1";
            self.nearest_ref = "" #nearest_ref "ENSMUST00000160944";
            self.transcripts_dict = {}
            self.exons_dict = {}

            if not tsv_line is None:
                self.set_gene_info(tsv_line)

        def set_gene_info(self, tsv_line):
            self.gene_info_set = True
            spln = tsv_line.strip().split("\t")
            self.chromosome = spln[0]
            self.source = spln[1]
            #self.start = spln[3]
            #self.end = spln[4]
            self.score = spln[5]
            self.strand = spln[6]
            self.frame = spln[7]

            #Apparently a few entries do not contain all these data types
            tmp_gene_id = re.findall(r'gene_id "(.*?)";', tsv_line)
            if len(tmp_gene_id) > 0:
                self.gene_id = tmp_gene_id[0]

            tmp_gene_version = re.findall(r'gene_version "(.*?)";', tsv_line)
            if len(tmp_gene_version) > 0:
                self.gene_version = tmp_gene_version[0]

            tmp_gene_name = re.findall(r'gene_name "(.*?)";', tsv_line)
            if len(tmp_gene_name) > 0:
                self.gene_name = tmp_gene_name[0]

            tmp_gene_source = re.findall(r'gene_source "(.*?)";', tsv_line)
            if len(tmp_gene_source) > 0:
                self.gene_source = tmp_gene_source[0]

            tmp_gene_biotype = re.findall(r'gene_biotype "(.*?)";', tsv_line)
            if len(tmp_gene_biotype) > 0:
                self.gene_biotype = tmp_gene_biotype[0]

            tmp = re.findall(r'oId "(.*?)";', tsv_line)
            if len(tmp) > 0:
                self.oId = tmp[0]
            tmp = re.findall(r'class_code "(.*?)";', tsv_line)
            if len(tmp) > 0:
                self.class_code = tmp[0]
            tmp = re.findall(r'tss_id "(.*?)";', tsv_line)
            if len(tmp) > 0:
                self.tss_id = tmp[0]
            tmp = re.findall(r'cov "(.*?)";', tsv_line)
            if len(tmp) > 0:
                self.cov = tmp[0]
            tmp = re.findall(r'nearest_ref "(.*?)";', tsv_line)
            if len(tmp) > 0:
                self.nearest_ref = tmp[0]


        def gene_info_is_set(self):
            return self.gene_info_set

        def add_transcript(self, transcript_name, transcript_obj):
            self.transcripts_dict.update({transcript_name: transcript_obj})

    class Transcript:

        def __init__(self, tsv_line=None):

            self.start = ""
            self.end = ""
            self.score = ""
            self.strand = ""
            self.chromosome = ""
            self.frame = ""
            self.gene_id = ""       # gene_id "XLOC_000001";
            self.transcript_id = "" # transcript_id "TCONS_00000001";
            self.FPKM = ""
            self.frac = ""
            self.conf_lo = ""
            self.conf_hi = ""
            self.class_code = ""
            self.cov = []
            self.gene_name = ""   #gene_name "Gm16088";
            self.oId = ""         #oId "ENSMUST00000160944";
            self.exons_dict = {}
            self.exon_list = []
            self.class_code = ""  #class_code "=";
            self.tss_id = ""      #tss_id "TSS1";
            self.nearest_ref = "" #nearest_ref "ENSMUST00000160944";

            if not tsv_line is None:
                self.set_transcript_info(tsv_line)


        def add_exon(self, tmp_exon_obj):
            #tmp_exon_obj = self.Exon(exon_line)
            self.exon_list.append(tmp_exon_obj)
            if self.start is None or self.start == "" or tmp_exon_obj.start < self.start:
                self.start = tmp_exon_obj.start
            if self.start is None or self.start == "" or tmp_exon_obj.end < self.start:
                self.start = tmp_exon_obj.end

            if self.end is None or self.end == "" or tmp_exon_obj.start > self.start:
                self.end = tmp_exon_obj.start
            if self.end is None or self.end == "" or tmp_exon_obj.end > self.end:
                self.end = tmp_exon_obj.end


        def set_transcript_info(self, tsv_line):

            spln = tsv_line.strip().split("\t")
            self.gene_info_set = True
            spln = tsv_line.strip().split("\t")
            self.chromosome = spln[0]
            self.source = spln[1]
            #self.start = spln[3]
            #self.end = spln[4]
            self.score = spln[5]
            self.strand = spln[6]
            self.frame = spln[7]

            tmp = re.findall(r'gene_id "(.*?)";', tsv_line)
            if len(tmp) > 0:
                self.gene_id = [0]
            tmp = re.findall(r'transcript_id "(.*?)";', tsv_line)
            if len(tmp) > 0:
                self.transcript_id = tmp[0]
            tmp = re.findall(r'FPKM "(.*?)";', tsv_line)
            if len(tmp) > 0:
                self.FPKM = tmp[0]
            tmp = re.findall(r'frac "(.*?)";', tsv_line)
            if len(tmp) > 0:
                self.frac = tmp[0]
            tmp = re.findall(r'conf_lo "(.*?)";', tsv_line)
            if len(tmp) > 0:
                self.conf_lo = tmp[0]
            tmp = re.findall(r'conf_hi "(.*?)";', tsv_line)
            if len(tmp) > 0:
                self.conf_hi = tmp[0]
            tmp = re.findall(r'cov "(.*?)";', tsv_line)
            if len(tmp) > 0:
                self.cov = tmp[0]
            tmp = re.findall(r'oId "(.*?)";', tsv_line)
            if len(tmp) > 0:
                self.oId = tmp[0]
            tmp = re.findall(r'class_code "(.*?)";', tsv_line)
            if len(tmp) > 0:
                self.class_code = tmp[0]
            tmp = re.findall(r'tss_id "(.*?)";', tsv_line)
            if len(tmp) > 0:
                self.tss_id = tmp[0]
            tmp = re.findall(r'cov "(.*?)";', tsv_line)
            if len(tmp) > 0:
                self.cov = tmp[0]
            tmp = re.findall(r'nearest_ref "(.*?)";', tsv_line)
            if len(tmp) > 0:
                self.nearest_ref = tmp[0]

    def transcripts(self):
        for tran_name in self.transcript_id_dict:
            yield self.transcript_id_dict[tran_name]

    def addline(self, tsv_line):
        '''1       Cufflinks       transcript      594459  597498  1       -       .
        gene_id "ENSG00000239664"; transcript_id "ENST00000357876"; FPKM "0.0000000000";
        frac "0.000000"; conf_lo "0.000000"; conf_hi "0.000000"; cov "0.000000"; full_read_support "no";
        '''

        if tsv_line[0] != "#":
            line_type = tsv_line.strip().split("\t")[2]
            if line_type == 'exon':
                gene_id = re.findall(r'gene_id "(.*?)";', tsv_line)[0]
                transcript_id = re.findall(r'transcript_id "(.*?)";', tsv_line)[0]

                if not gene_id in self.gene_id_dict:
                    self.gene_id_dict.update({gene_id: self.Gene(tsv_line)})

                if not transcript_id in self.gene_id_dict[gene_id].transcripts_dict:
                    tmp_transcript = self.Transcript(tsv_line)

                    self.gene_id_dict[gene_id].transcripts_dict.update({transcript_id: tmp_transcript})
                    self.transcript_id_dict.update({transcript_id: tmp_transcript})

                tmp_exon = self.Exon(tsv_line)
                self.gene_id_dict[gene_id].add_exon(tmp_exon)
                self.gene_id_dict[gene_id].transcripts_dict[transcript_id].add_exon(tmp_exon)

            else:
                print("error", line_type, tsv_line)


class CufflinksGTF:

    def __init__(self, gtf_file_name):
        self.transcript_id_dict = {}
        self.o = 0
        self.t = 0
        self.chromosome_then_ordered_dict = {}
        self.gene_id_dict = {}

        for line in open(gtf_file_name):
            self.addline(line)

    class Transcript:

        #def exons(self):
        #    for el in self.exon_list:
        #        yield el

        def __init__(self):
            self.start = ""
            self.end = ""
            self.score = ""
            self.strand = ""
            self.frame = ""

            self.gene_id = ""
            self.transcript_id = ""

            self.FPKM = ""
            self.frac = ""
            self.conf_lo = ""
            self.conf_hi = ""
            self.cov = []

        def set_transcript_info(self, tsv_line):

            spln = tsv_line.strip().split("\t")
            self.start = spln[3]
            self.end = spln[4]
            self.score = spln[5]
            self.strand = spln[6]
            self.frame = spln[7]

            tmp = re.findall(r'gene_id "(.*?)";', tsv_line)
            if len(tmp) > 0:
                self.gene_id = [0]

            tmp = re.findall(r'transcript_id "(.*?)";', tsv_line)
            if len(tmp) > 0:
                self.transcript_id = tmp[0]

            tmp = re.findall(r'FPKM "(.*?)";', tsv_line)
            if len(tmp) > 0:
                self.FPKM = tmp[0]

            tmp = re.findall(r'frac "(.*?)";', tsv_line)
            if len(tmp) > 0:
                self.frac = tmp[0]

            tmp = re.findall(r'conf_lo "(.*?)";', tsv_line)
            if len(tmp) > 0:
                self.conf_lo = tmp[0]

            tmp = re.findall(r'conf_hi "(.*?)";', tsv_line)
            if len(tmp) > 0:
                self.conf_hi = tmp[0]

            tmp = re.findall(r'cov "(.*?)";', tsv_line)
            if len(tmp) > 0:
                self.cov = tmp[0]

        #def add_exon(self, exon_name):
        #    self.exon_list.append(exon_name)
    #class Exon:
    #    def __init__(self, tsv_line):
    #        spln = tsv_line.strip().split("\t")
    #        self.start = spln[3]
    #        self.end = spln[4]
    #        self.exon_number = re.findall(r'exon_number "(.*?)";', tsv_line)[0]
    #        self.exon_id = re.findall(r'exon_id "(.*?)";', tsv_line)[0]
    #        self.exon_version = re.findall(r'exon_version "(.*?)";', tsv_line)[0]

    def transcripts(self):
        for tran_name in self.transcript_id_dict:
            yield self.transcript_id_dict[tran_name]

    def addline(self, tsv_line):
        '''1       Cufflinks       transcript      594459  597498  1       -       .
        gene_id "ENSG00000239664"; transcript_id "ENST00000357876"; FPKM "0.0000000000";
        frac "0.000000"; conf_lo "0.000000"; conf_hi "0.000000"; cov "0.000000"; full_read_support "no";
        '''

        if tsv_line[0] != "#":
            spln = tsv_line.strip().split("\t")

            try:
                line_type = spln[2]
            except:
                line_type = "unknown"

            if line_type == 'transcript':
                transcript_id = re.findall(r'transcript_id "(.*?)";', tsv_line)[0]
                if not transcript_id in self.transcript_id_dict:
                    self.transcript_id_dict.update({transcript_id: self.Transcript()})
                    self.transcript_id_dict[transcript_id].set_transcript_info(tsv_line)
                else:
                    tmp_t = self.Transcript()
                    tmp_t.set_transcript_info(tsv_line)
                    if self.transcript_id_dict[transcript_id].FPKM < tmp_t.FPKM:
                        self.transcript_id_dict[transcript_id] = tmp_t



            else:
                if not line_type in set(('exon', 'CDS', 'UTR', 'start_codon', 'stop_codon', 'Selenocysteine')):
                    print("error", line_type)


class EnsemblGTF:

    def __init__(self, gtf_file_name, is_file=True):

        self.sequence_features = {"gene": {}, "transcript": {}, "exon": {}}
        self.chromosome_then_ordered_dict = {}
        self.gene_id_dict = {}

        if is_file:
            for line in open(gtf_file_name):
                self.addline(line)
        else:
            for line in gtf_file_name:#.split("\n"):
                self.addline(line)


    class Gene:

        def transcripts(self):
            for el in self.transcripts_dict:
                yield self.transcripts_dict[el]

        def add_exon(self, exon_name, exon_obj):
            if not exon_name in self.exons_dict:
                self.exons_dict.update({exon_name: exon_obj})

        def __init__(self, tsv_line=None):
            self.gene_info_set = False
            self.chromosome = ""
            self.source = ""
            self.start = ""
            self.end = ""
            self.score = ""
            self.strand = ""
            self.frame = ""
            self.gene_id = ""
            self.gene_version = ""
            self.gene_name = ""
            self.gene_source = ""
            self.gene_biotype = ""
            self.transcripts_dict = {}
            self.exons_dict = {}

            if not tsv_line is None:
                self.set_gene_info(tsv_line)

        def getloctuple(self):
            return ((self.start, self.end), )

        def set_gene_info(self, tsv_line):
            self.gene_info_set = True
            spln = tsv_line.strip().split("\t")
            self.chromosome = spln[0]
            self.source = spln[1]
            self.start = spln[3]
            self.end = spln[4]
            self.score = spln[5]
            self.strand = spln[6]
            self.frame = spln[7]

            #Apparently a few entries do not contain all these data types
            tmp_gene_id = re.findall(r'gene_id "(.*?)";', tsv_line)
            if len(tmp_gene_id) > 0:
                self.gene_id = tmp_gene_id[0]

            tmp_gene_version = re.findall(r'gene_version "(.*?)";', tsv_line)
            if len(tmp_gene_version) > 0:
                self.gene_version = tmp_gene_version[0]

            tmp_gene_name = re.findall(r'gene_name "(.*?)";', tsv_line)
            if len(tmp_gene_name) > 0:
                self.gene_name = tmp_gene_name[0]

            tmp_gene_source = re.findall(r'gene_source "(.*?)";', tsv_line)
            if len(tmp_gene_source) > 0:
                self.gene_source = tmp_gene_source[0]

            tmp_gene_biotype = re.findall(r'gene_biotype "(.*?)";', tsv_line)
            if len(tmp_gene_biotype) > 0:
                self.gene_biotype = tmp_gene_biotype[0]


        def gene_info_is_set(self):
            return self.gene_info_set

        def add_transcript(self, transcript_name, transcript_obj):
            self.transcripts_dict.update({transcript_name: transcript_obj})

    class Transcript:

        def exons(self):
            for el in self.exon_list:
                yield el

        def __init__(self):
            self.start = ""
            self.end = ""
            self.score = ""
            self.strand = ""
            self.frame = ""
            self.transcript_id = ""
            self.transcript_version = ""
            self.transcript_name = "";
            self.transcript_source = ""
            self.transcript_biotype = ""
            self.exon_list = []

        def set_transcript_info(self, tsv_line):

            spln = tsv_line.strip().split("\t")
            self.start = spln[3]
            self.end = spln[4]
            self.score = spln[5]
            self.strand = spln[6]
            self.frame = spln[7]

            tmp_transcript_id = re.findall(r'transcript_id "(.*?)";', tsv_line)
            if len(tmp_transcript_id) > 0:
                self.transcript_id = tmp_transcript_id[0]

            tmp_transcript_version = re.findall(r'transcript_version "(.*?)";', tsv_line)
            if len(tmp_transcript_version) > 0:
                self.transcript_version = tmp_transcript_version[0]

            tmp_transcript_name = re.findall(r'transcript_name "(.*?)";', tsv_line)
            if len(tmp_transcript_name) > 0:
                self.transcript_name = tmp_transcript_name[0]

            tmp_transcript_source = re.findall(r'transcript_source "(.*?)";', tsv_line)
            if len(tmp_transcript_source) > 0:
                self.transcript_source = tmp_transcript_source[0]

            tmp_transcript_biotype = re.findall(r'transcript_biotype "(.*?)";', tsv_line)
            if len(tmp_transcript_biotype) > 0:
                self.transcript_biotype = tmp_transcript_biotype[0]

        def add_exon(self, exon_name):
            self.exon_list.append(exon_name)

    class Exon:
        def __init__(self, tsv_line):
            spln = tsv_line.strip().split("\t")
            self.start = spln[3]
            self.end = spln[4]
            self.exon_number = re.findall(r'exon_number "(.*?)";', tsv_line)[0]
            self.exon_id = re.findall(r'exon_id "(.*?)";', tsv_line)[0]
            try:
                self.exon_version = re.findall(r'exon_version "(.*?)";', tsv_line)[0]
            except:
                self.exon_version = ""

    def addline(self, tsv_line):
        '''
        1       havana  gene    11869   14409   .       +       .       gene_id "ENSG00000223972"; gene_version "5"; gene_name "DDX11L1"; gene_source "havana"; gene_biotype "transcribed_unprocessed_pseudogene";
        1       havana  exon    11869   12227   .       +       .       gene_id "ENSG00000223972"; gene_version "5"; transcript_id "ENST00000456328"; transcript_version "2"; exon_number "1"; gene_name "DDX11L1"; gene_source "havana"; gene_biotype "transcribed_unprocessed_pseudogene"; transcript_name "DDX11L1-002"; transcript_source "havana"; transcript_biotype "processed_transcript"; exon_id "ENSE00002234944"; exon_version "1";
        1       havana  exon    12613   12721   .       +       .       gene_id "ENSG00000223972"; gene_version "5"; transcript_id "ENST00000456328"; transcript_version "2"; exon_number "2"; gene_name "DDX11L1"; gene_source "havana"; gene_biotype "transcribed_unprocessed_pseudogene"; transcript_name "DDX11L1-002"; transcript_source "havana"; transcript_biotype "processed_transcript"; exon_id "ENSE00003582793"; exon_version "1";
        1       havana  exon    13221   14409   .       +       .       gene_id "ENSG00000223972"; gene_version "5"; transcript_id "ENST00000456328"; transcript_version "2"; exon_number "3"; gene_name "DDX11L1"; gene_source "havana"; gene_biotype "transcribed_unprocessed_pseudogene"; transcript_name "DDX11L1-002"; transcript_source "havana"; transcript_biotype "processed_transcript"; exon_id "ENSE00002312635"; exon_version "1";
        1       havana  transcript      12010   13670   .       +       .       gene_id "ENSG00000223972"; gene_version "5"; transcript_id "ENST00000450305"; transcript_version "2"; gene_name "DDX11L1"; gene_source "havana"; gene_biotype "transcribed_unprocessed_pseudogene"; transcript_name "DDX11L1-001"; transcript_source "havana"; transcript_biotype "transcribed_unprocessed_pseudogene";
        1       havana  exon    12010   12057   .       +       .       gene_id "ENSG00000223972"; gene_version "5"; transcript_id "ENST00000450305"; transcript_version "2"; exon_number "1"; gene_name "DDX11L1"; gene_source "havana"; gene_biotype "transcribed_unprocessed_pseudogene"; transcript_name "DDX11L1-001"; transcript_source "havana"; transcript_biotype "transcribed_unprocessed_pseudogene"; exon_id "ENSE00001948541"; exon_version "1";
        1       havana  exon    12179   12227   .       +       .       gene_id "ENSG00000223972"; gene_version "5"; transcript_id "ENST00000450305"; transcript_version "2"; exon_number "2"; gene_name "DDX11L1"; gene_source "havana"; gene_biotype "transcribed_unprocessed_pseudogene"; transcript_name "DDX11L1-001"; transcript_source "havana"; transcript_biotype "transcribed_unprocessed_pseudogene"; exon_id "ENSE00001671638"; exon_version "2";
        '''
        if tsv_line[0] != "#":
            spln = tsv_line.strip().split("\t")
            line_type = spln[2]
            gene_id = re.findall(r'gene_id "(.*?)";', tsv_line)[0]
            if not gene_id in self.gene_id_dict:
                self.gene_id_dict.update({gene_id: self.Gene()})
            if line_type == 'gene':
                #If gene info not set then add info
                #if not self.gene_id_dict[gene_id].gene_info_is_set
                self.gene_id_dict[gene_id].set_gene_info(tsv_line)
            elif line_type == 'transcript':
                transcript_id = re.findall(r'transcript_id "(.*?)";', tsv_line)[0]
                if not transcript_id in self.gene_id_dict[gene_id].transcripts_dict:
                    self.gene_id_dict[gene_id].transcripts_dict.update({transcript_id: self.Transcript()})
                self.gene_id_dict[gene_id].transcripts_dict[transcript_id].set_transcript_info(tsv_line)
            elif line_type == 'exon':
                transcript_id = re.findall(r'transcript_id "(.*?)";', tsv_line)[0]
                #exon_id = re.search(r'exon_id "(.*?)";', tsv_line)
                if not transcript_id in self.gene_id_dict[gene_id].transcripts_dict:
                    #Add transcript
                    self.gene_id_dict[gene_id].transcripts_dict.update({transcript_id: self.Transcript()})
                #add exon
                tmp_exon_obj = self.Exon(tsv_line)
                self.gene_id_dict[gene_id].transcripts_dict[transcript_id].add_exon(tmp_exon_obj)
                self.gene_id_dict[gene_id].add_exon(tmp_exon_obj.exon_id, tmp_exon_obj)

            else:
                if not line_type in set(('CDS', 'UTR', 'start_codon', 'stop_codon', 'Selenocysteine')):
                    print("error", line_type)



class IDMapper:

    def __init__(self, gtf_file):

        self.get_children = {}
        self.get_parent = {}

        for line in open(gtf_file):
            if line[0] != "#" and line.split()[2] == "transcript":
                transcript_id = re.findall(r'transcript_id "(.*?)";', line)[0]
                gene_id = re.findall(r'gene_id "(.*?)";', line)[0]

                if not transcript_id in self.get_parent:
                    self.get_parent.update({transcript_id: gene_id})

