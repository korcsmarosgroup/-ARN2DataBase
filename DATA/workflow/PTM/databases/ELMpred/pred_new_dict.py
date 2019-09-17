'''
Maps ELMs to their protein IDs and the interacting domain's protein ID and inserts the two into an SQL database.
 :argument: EXPORT_DB_LOCATION: saving location of the final database
 :argument: ELMS_FILE: all ELM classes of the four used species in a .tsv files: http://elm.eu.org/classes/
 :argument: INT_DOMAINS_FILE: files containing ELM names and their interacting domain PFAM ids in a .tsv files: http://elm.eu.org/interactiondomains
 :argument: PROT_LIST: list of files for each species used, containing their whole proteomes from UniProt in .fa files
'''

# Imports
import csv, sqlite3, os
import re, logging
from itertools import groupby

# Defining constants
DB_TYPE = 'ELM'
EXPORT_DB_LOCATION = '../../output/ELM.db'
ELMS_FILE = 'PTM/databases/ELMpred/files/elm_classes.tsv'
INT_DOMAINS_FILE = 'PTM/databases/ELMpred/files/elm_interaction_domains.tsv'
PFAM_FILE_LIST = ['PTM/databases/ELMpred/files/homo_pfam.txt',
                  'PTM/databases/ELMpred/files/drosi_pfam.txt',
                  'PTM/databases/ELMpred/files/celegans_pfam.txt',
                  'PTM/databases/ELMpred/files/danio_pfam.txt'
                  ]

PDB_LIST = ['PTM/databases/ELMpred/files/homo_pdb.txt',
            'PTM/databases/ELMpred/files/drosi_pdb.txt',
            'PTM/databases/ELMpred/files/danio_pdb.txt',
            'PTM/databases/ELMpred/files/celegans_pdb.txt']
pred_db = 'ELM_pred.db'

dssp_file_list = []
logging.basicConfig(level=logging.DEBUG)

conn = sqlite3.connect(pred_db)

"""
# Amandának
PDB_LIST = ['files/homo_pdb.txt']
PFAM_FILE_LIST = ['files/homo_pfam.txt']
file_list = ['files/uniprot_homo_seq.tab']
mediators = 'files/mediators_Luca_list.txt'
autophagy = 'files/ARN_core_Luca.txt'
INT_DOMAINS_FILE = 'files/elm_interaction_domains.tsv'
ELMS_FILE = 'files/elm_classes.tsv'
output_file = 'arn_mediators2.tsv'

"""

# For Aggie
PDB_LIST = ['files/homo_pdb.txt']
PFAM_FILE_LIST = ['files/homo_pfam.txt', 'files/mouse_pfam.txt']
file_list = ['files/uniprot_homo_seq.tab', 'files/uniprot_mouse_seq.tab']
INPUT_FILE = 'files/Aggie_Selected_candidates_EvoDis.tsv'
ELMS_FILE = 'files/elm_classes.tsv'
INT_DOMAINS_FILE = 'files/elm_interaction_domains.tsv'
output_file = 'Aggie_ELM_pred_motif_proteins.tsv'
output_file2 = 'Aggie_ELM_pred_int_proteins.tsv'

def motif_to_regex():
    """
        Creates dictionary from ELMS_FILE that has ELM motif names as keys and their regex seqs as values.
    :return: motif_regex_dict
    """

    motif_regex_dict = {}
    with open(ELMS_FILE) as motifs:
        motifs.readline()
        for line in motifs:
            line = line.strip().split('\t')

            motif_name = line[1].replace('"', '')
            regex_seq = line[4].replace('"', '')

            motif_regex_dict[motif_name] = regex_seq

    return motif_regex_dict


def uniprot_to_pdb(pdb_filename):
    """
        Creates dictionary from files of PDB_LIST that has uniprot ids as keys and pdb ids as a list of values.
    :return: uniprot_domain_dict
    """

    uniprot_domain_dict = {}

    with open(pdb_filename) as pdbs:
        pdbs.readline()
        for line in pdbs:
            line = line.strip().split('\t')

            uniprot_id = line[0]

            if len(line) > 2:
                pdb_id = line[2].split(';')
            else:
                pdb_id = []

            uniprot_domain_dict[uniprot_id] = pdb_id

    return uniprot_domain_dict


def domain_to_motif():
    """
            Creates dictionary from INT_DOMAINS_FILE that has motif names as values and their bindable pfam domains as keys.
    :return: motif_domain_dict
    """

    motif_domain_dict = {}

    with open(INT_DOMAINS_FILE) as pfamfile:
        pfamfile.readline()
        for line in pfamfile:
            line = line.strip().split('\t')

            if len(line) > 1:
                motif_name = line[0].replace('"', '')
                pfam_name = line[1].replace('"', '')

                if pfam_name not in motif_domain_dict:
                    motif_domain_dict[pfam_name] = [motif_name]
                else:
                    motif_domain_dict[pfam_name].append(motif_name)

    return motif_domain_dict


def uniprot_to_domain(pfam_filename):
    """
            Creates dictionary from files of PFAM_FILE_LIST that has uniprot ids as keys and their pfam domains as values.
    :return: uniprot_domain_dict
    """

    uniprot_domain_dict = {}

    with open(pfam_filename) as domainfile:
        domainfile.readline()
        for line in domainfile:
            line = line.strip().split('\t')

            uniprot_id = line[0]
            if len(line) > 3:
                pfam_ids = line[3].strip().split(';')
            else:
                pfam_ids = []

            if uniprot_id not in uniprot_domain_dict:
                uniprot_domain_dict[uniprot_id] = pfam_ids
            else:
                for pfam in pfam_ids:
                    uniprot_domain_dict[uniprot_id].append(pfam)

    return uniprot_domain_dict


def motif_to_uniprot():
    motif_uniprot_dict = {}

    counter = 0
    # for files in os.listdir('dssp/LAB/'):
    #     dssp_file_list.append('dssp/LAB/' + files)
    #     counter += 1
    #     if counter == 100:
    #         break

    # Getting sequence data from dssp
    # for filename in dssp_file_list:
    #     with open(filename) as dsspfile, \
    #             open(ELMS_FILE) as elms, \
    #             open(file_list[0]) as proteome:
    #         for line in dsspfile:
    #             if line[2] == '#':
    #                 break
    #         seq = ''
    #         for row in dsspfile:
    #             seq += row[13].upper()

    with open(file_list[0]) as proteome:
        proteome.readline()
        for line in proteome:
            line = line.strip().split('\t')
            counter +=1
            # if counter == 1000:
            #     break

            uniprot = line[0]
            seq = line[4]

            with open(ELMS_FILE) as elms:
                elms.readline()
                for elm_line in elms:
                    elm_line = elm_line.split('\t')
                    regex = r'%s' % elm_line[4].replace('"', '')

                    matches = re.finditer(regex, seq)

                    for matchNum, match in enumerate(matches):
                            # print("Match {matchNum} was found at {start}-{end}: {match}".format(matchNum=matchNum, start=match.start(),
                            # end=match.end(), match=match.group()), line[1])
                            if elm_line[1].replace('"', '') not in motif_uniprot_dict:
                                motif_uniprot_dict[elm_line[1].replace('"', '')] = [uniprot]
                            else:
                                motif_uniprot_dict[elm_line[1].replace('"', '')].append(uniprot)

    return motif_uniprot_dict


def sequence_to_uniprot(proteomefile):
    """
               Creates dictionary from files of file_list that has protein sequences as keys and the protein's uniprot id
                as values.
       :return: seq_uniprot_dict
    """

    seq_uniprot_dict = {}

    with open(proteomefile) as protseq:
        protseq.readline()
        for line in protseq:
            line = line.strip().split('\t')
            uniprot = line[0]
            sequence = line[4]

            seq_uniprot_dict[sequence] = uniprot

    return seq_uniprot_dict


def main():

    my_motif_list = []

    # Calling functions
    mot_regex = motif_to_regex()
    for file in PFAM_FILE_LIST:
        uni_domain = uniprot_to_domain(file)
    dom_mot = domain_to_motif()
    mot_uni = motif_to_uniprot()


    # SLK3 run
    # creating preddb table
    with conn:
        c = conn.cursor()
        c.execute("DROP TABLE if EXISTS elm_to_prot")
        c. execute('''CREATE TABLE elm_to_prot (id INTEGER PRIMARY KEY ,
                                                elm_name CHAR(100),
                                                elm_regex CHAR(100),
                                                elm_prot_id CHAR(100),
                                                taxid CHAR(100),
                                                elm_domain CHAR(100),
                                                domain_prot_id CHAR (100))''')

        # Adding regex sequences and motif names to the preddb
        # the different regex expressions assigned to one motif will be separated by '|'
        for motif in mot_regex.keys():
            c.execute('INSERT INTO elm_to_prot(elm_name, elm_regex) VALUES (?,?)',
                      (motif, '|'.join(mot_regex[motif])))

        # Adding uniprot ids of the protein containing the motif
        # If a motif is in multiple proteins, they will be separated by '|' symbol
        for motif in mot_uni.keys():
            c.execute('''INSERT INTO elm_to_prot(elm_prot_id) VALUES (?)
                         WHERE elm_to_prot.elm_name = %s''',
                      ('|'.join(mot_uni[motif])))
    with open(INPUT_FILE) as infile1:
        infile1.readline()
        for line in infile1:
            line = line.strip().split('\t')
            my_motif = line[2].replace('"', '')

            my_motif_list.append(my_motif)
    """
    Amandának
        for line in infile2:
            line = line.strip().split('\t')
            domain_protein = line[0].replace('"', '')

            domain_prot_list.append(domain_protein)

    file_line = []

    for protein in motif_prot_list:
        # Getting pfam domains of each protein
        my_domains = uni_domain[protein]
        # Getting interacting motifs for each domain
        for domain in my_domains:
            if domain != '' and domain in dom_mot:
                interacting_motifs = dom_mot[domain]
                # Getting uniprot id of proteins containing interacting motifs
                for motif in interacting_motifs:
                    if motif in mot_uni:
                        motif_prot_ids = mot_uni[motif]
                        # Assembling line for writing to output file
                        for int_prot in motif_prot_ids:
                            if int_prot in domain_prot_list:
                                ass_line = protein+'\t'+domain+'\t'+motif+'\t'+int_prot+'\n'
                                if ass_line not in file_line:
                                    file_line.append(ass_line)
    """
# For Aggie

    mot_file_line = []
    int_file_line = []
    for motif in my_motif_list:
        if motif in mot_uni.keys():
            # Getting protein uniprotids of each motif
            my_proteins = mot_uni[motif]
            # Assembling line for output file, adding it to a list
            mot_prot_line = motif + '\t' + '|'.join(my_proteins) + '\n'
            if mot_prot_line not in mot_file_line:
                mot_file_line.append(mot_prot_line)

    for motif in my_motif_list:
        # Getting domains that interact with my motif
        my_domain = []
        for dom, mot in dom_mot.items():
            if motif in mot:
                my_domain.append(dom)
        # Getting proteins that contain the found domains
        my_prot = []
        for domain in my_domain:
            for uni, dom in uni_domain.items():
                if domain in dom:
                    my_prot.append(uni)
            # Assembling line for output file
            int_prot_line = motif + '\t' + domain + '\t' + '|'.join(my_prot) + '\n'
            if int_prot_line not in int_file_line:
                int_file_line.append(int_prot_line)

    # Deleting output file if it exists
    if os.path.exists(output_file):
        os.remove(output_file)
    if os.path.exists(output_file2):
        os.remove(output_file2)
    with open(output_file, 'w') as outfile, \
            open(output_file2, 'w') as outfile2:
        # Adding header
        outfile.write('Motif\tProteins\n')
        # Adding lines
        for elem in mot_file_line:
            outfile.write(elem)

        outfile2.write('Motif\tDomain\tProtein\n')
        for element in int_file_line:
            outfile2.write(element)


if __name__ == '__main__':
    main()
