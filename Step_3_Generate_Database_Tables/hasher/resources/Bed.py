class Parse:

    class Feature:

        def __init__(self, feature_line):
            """
            :param feature_line:
            :return:
            """
            spln = feature_line.strip().split()
            self.chromosome = spln[0].strip("chr")
            self.start = spln[1]
            self.end = spln[2]
            self.strand = "."
            self.name = spln[3]
            if len(spln) > 4:
                self.strand = spln[5]

        def getloctuple(self):
            return ( (self.start,self.end), )

    def __init__(self, bed_text):
        """
        :param bed_file_name:
        :return:
        """
        self.bed_list = []
        self.bed_dict = {}
        for line in bed_text:
            tmp_feature = self.Feature(line)
            self.bed_list.append(tmp_feature)
            self.bed_dict.update({tmp_feature.name: tmp_feature})





    def getgenedict(self):

        return self.bed_dict