from ftplib import FTP
import time
import random


def getftpfilesize(ftp_link, debug=False):
    """ This function retrieves file sizes for a set of files in a directory of an FTP server.
    :param ftp_link: The link with the file name included ex:
    ftp://ftp-trace.ncbi.nlm.nih.gov/sra/sra-instant/reads/ByExp/sra/SRX/SRX251/SRX251962/SRR786467/SRR786467.sra
    :param debug: FTPs servers can be finiky, for easy troubleshooting.
    :return: An integer representing a file size.
    """
    # Links will look like this.
    # 'ftp://ftp-trace.ncbi.nlm.nih.gov/sra/sra-instant/reads/ByExp/sra/SRX/SRX251/SRX251962/SRR786467/SRR786467.sra'
    ftp_server = ftp_link.split("ftp://")[-1].split("/")[0]
    file_name = ftp_link.split("/")[-1]
    file_path = "/".join(ftp_link.split("ftp://")[-1].split("/")[1:-1])

    if debug:
        print(ftp_server)
        print(file_name)
        print(file_path)

    ftp = FTP(ftp_server)
    ftp.login()
    ftp.cwd(file_path)

    # There can be more than one file in a directory, even for the SRA archive.
    lines = []
    ftp.retrlines("LIST", lines.append)

    file_size = ""
    # Iterate over the files in the directory.
    for line in lines:

        if debug:
            print(line)

        # Return the size of the file queried.
        if file_name in line:
            file_size = int(line.split()[-5])

    # Make sure we see a file in the directory.
    assert file_size is not ""

    return file_size


def getfastqmeanandstdev(file_name):
    """Planned for future use to find the read length of fastq files.
    :param file_name:
    :return:
    """
    i = 0
    time.sleep(random.randint(1, 1))
    # In our case all fastq lines will be the same length.
    mean_len = 0
    stdev = 1
    for line in open(file_name):
        if i >= 1:
            mean_len = len(line.strip())
            break
        i += 1

    return mean_len, stdev


def filelen(file_name):
    """ Simply find the number of lines in a file.
    :param file_name:
    :return:
    """
    line_len = 0
    with open(file_name) as f:
        for line_i, l in enumerate(f):
            line_len = line_i
            pass
    return line_len + 1
