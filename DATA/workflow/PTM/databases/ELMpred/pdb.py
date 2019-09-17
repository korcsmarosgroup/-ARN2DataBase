'''
Checks coverage od PDB in uniprot proteomes for all organisms.
'''

SPEC_LIST = ['files/celegans_pdb.txt',
             'files/danio_pdb.txt',
             'files/drosi_pdb.txt',
             'files/homo_pdb.txt']

for spec in SPEC_LIST:
    non_count = 0
    line_count = 0
    with open(spec) as infile:
        infile.readline()
        for line in infile:
            line_count = line_count + 1
            line = line.split('\t')
            taxid = line[1]
            if line[2] == '\n':
                non_count = non_count +1
        print(taxid, line_count, non_count)