'''
Maps ELMs to their protein IDs and the interacting domain's protein ID and inserts the two into an SQL database.
 :argument: EXPORT_DB_LOCATION: saving location of the final database
 :argument: ELMS_FILE: all ELM classes of the four used species in a .tsv files: http://elm.eu.org/classes/
 :argument: INT_DOMAINS_FILE: files containing ELM names and their interacting domain PFAM ids in a .tsv files: http://elm.eu.org/interactiondomains
 :argument: PROT_LIST: list of files for each species used, containing their whole proteomes from UniProt in .fa files
'''

# Imports
import csv, os
from SLKlib.SQLiteDBApi.sqlite_db_api import PsimiSQL
import re, logging
from dataclasses import dataclass, field
from typing import List
from functools import lru_cache
from collections import defaultdict

# Defining constants
SQL_SEED = '../../SLKlib/SQLiteDBApi/network-db-seed.sql'
DB_TYPE = 'ELM'
EXPORT_DB_LOCATION = '../../output/ELM.db'
ELMS_FILE = 'PTM/databases/ELMpred/files/elm_classes.tsv'
INT_DOMAINS_FILE = 'PTM/databases/ELMpred/files/elm_interaction_domains.tsv'
UNIPROT_DATA_FILE = 'PTM/databases/ELMpred/files/uniprot_9606,7227,6239,7955_entry,taxid,pdb,pfam.tsv'
UNIPROT = {}
pred_db = 'ELM_pred.db'
file_list = []
logging.basicConfig(level=logging.DEBUG)
qsse_dict = {
    'E': 0.35,
    'H': 0.55,
    'I': 0.55,
    'B': 1.5,
    'T': 1.5,
    'S': 1.5,
    'U': 1.5,
    'G': 1.33,
    ' ': 0.0,
}
# Residue max accessibility
Miller = {
    'A': 113.0,
    'R': 241.0,
    'N': 158.0,
    'D': 151.0,
    'B': 154.5,
    'C': 140.0,
    'Q': 189.0,
    'E': 183.0,
    'G': 85.0,
    'H': 194.0,
    'I': 182.0,
    'L': 180.0,
    'K': 211.0,
    'M': 204.0,
    'F': 218.0,
    'P': 143.0,
    'S': 122.0,
    'T': 146.0,
    'W': 259.0,
    'Y': 229.0,
    'V': 160.0,
}


@dataclass
class ELMmatch:
    elm_name: str = field(default_factory=lambda: "")
    elm_start: int = field(default_factory=lambda: -1)
    elm_end: int = field(default_factory=lambda: -1)
    elm_seq: str = field(default_factory=lambda: "")
    Qand: int = field(default_factory=lambda: 0)
    elm_prot_id: List = field(default_factory=lambda: [])
    taxid: int = field(default_factory=lambda: 0)
    elm_domain: List = field(default_factory=lambda: [])
    domain_prot_id: List = field(default_factory=lambda: [])
    dssp_file: str = field(default_factory=lambda: "")
    pdb: str = field(default_factory=lambda: "")
ELMmaches = []


@dataclass
class DSSPline:
    position: int
    letter: str
    sec_str: str
    QACC: int
    QSSE: float
    Accessibility: float


def get_match(filename):
    # Getting ELM data
    #elms = csv.reader(open(ELMS_FILE), delimiter='\t')
    #next(elms)

    #Getting sequence data from dssp
    with open(filename) as dsspfile:
        for line in dsspfile:
            if line[2] == '#':
                break
        seq = ''
        for row in dsspfile:
            seq += row[13].upper()
        #Using RegEx algorithm to find ELM matches in the dssp sequence
        with open(ELMS_FILE) as elms:
            for line in elms:
                if line[0] == "#":
                    continue
                line = line.strip().split('\t')
                regex = r'%s' % line[4].replace('"','')
                matches = re.finditer(regex, seq)
                for matchNum, match in enumerate(matches):
                    match = ELMmatch(
                        elm_name=line[1].replace('"',''),
                        elm_start=match.start(),
                        elm_end=match.end(),
                        elm_seq=match.group(),
                        dssp_file=filename,
                        pdb=str(os.path.basename(filename).split(".")[0]),
                    )
                    ELMmaches.append(match)
                    #print("Match {matchNum} was found at {start}-{end}: {match}".format(matchNum=matchNum, start=match.start(),
                    #end=match.end(), match=match.group()), line[1])


@lru_cache(maxsize=None)
def proc_dssp(dsspfilename):
    dssp = []
    with open(dsspfilename) as dsspfile:
        for line in dsspfile:
            if line[2] == '#':
                break
        for row in dsspfile:
            aa = row[13].upper()
            qacc = int(row[35:38].strip())
            rel_acc = 0
            if aa in Miller.keys():
                qacc = int(row[35:38].strip())
                rel_acc = qacc / Miller[aa]
            dssp.append(DSSPline(
                position=int(row[0:6].strip()),
                letter=aa,
                sec_str=row[16],
                QACC=qacc,
                QSSE=qsse_dict[row[16]],
                Accessibility=rel_acc,
            ))
    return dssp

def get_scores():
    # SELECT elm_name, elm_start, elm_end, elm_seq FROM elm_to_prot
    for m in ELMmaches:
        qsse_match = 0
        qacc_match = 0
        dssp = proc_dssp(m.dssp_file)
        match_lenght = len(m.elm_seq)
        for seq_pos in range(m.elm_start, m.elm_end+1):
            qsse_match += dssp[seq_pos-1].QSSE
            qacc_match += dssp[seq_pos-1].QACC
        Qsse = qsse_match / match_lenght
        Qacc = qacc_match / match_lenght
        m.Qand = Qsse + Qacc


def get_protein_id():
    """
        Converts dssp pdb files names to uniprot ids
        :return:
    """
    for m in ELMmaches:
        for u in UNIPROT["pdb2uniprot"][m.pdb]:
            m.elm_prot_id.append(u)

    logging.debug('Protein id done')


def get_domain():

    # Getting domain data
    domains = csv.reader(open(INT_DOMAINS_FILE), delimiter='\t')
    next(domains)
    ELM2domain = {}
    for line in domains:
        pfamid = line[1]
        elmname = line[0]
        if elmname not in ELM2domain:
            ELM2domain[elmname] = []
        ELM2domain[elmname].append(pfamid)

    for m in ELMmaches:
        if m.elm_name in ELM2domain:
            m.elm_domain = ELM2domain[m.elm_name].copy()
            for d in m.elm_domain:
                for u in UNIPROT["pfam2uniprot"][d]:
                    if UNIPROT["uniprotac2taxid"][u] == m.taxid:
                        m.domain_prot_id.append(u)
    logging.debug('Domain done')


def get_taxid():
    for m in ELMmaches:
        taxid = None
        for u in m.elm_prot_id:
            if u in UNIPROT["uniprotac2taxid"]:
                taxid = UNIPROT["uniprotac2taxid"][u]
        m.taxid = taxid



def insert_or_get_node_dict(id, idtype, taxid, node_names_to_id, db_api):
    node_dict = {
        "name": idtype.strip() + ':' + id.strip(),
        "tax_id": taxid,
        "alt_accession": None,
        'pathways': None,
        "aliases": None,
        "topology": None
    }

    if not re.search("^[/\\.\\w-]+$", id):
        print("WARNING: malformed node id: " + node_dict['name'])
        return None

    if node_dict['name'] in node_names_to_id:
        node_dict['id'] = node_names_to_id[node_dict['name']]
    else:
        db_api.insert_unique_node(node_dict)
        node_names_to_id[node_dict['name']] = node_dict['id']

    return node_dict


def loadUniprotFile(filename):
    UNIPROT["uniprotac2taxid"] = {}
    UNIPROT["pdb2uniprot"] = defaultdict(list)
    UNIPROT["pfam2uniprot"] = defaultdict(list)
    with open(filename) as f:
        f.readline()
        for line in f:
            cells = line.strip().split("\t")
            if len(cells) != 4:
                continue
            uniprotac = cells[0]
            taxid = int(cells[1])
            pdbs = [c for c in cells[2].split(";") if c != ""]
            pfams = [c for c in cells[3].split(";") if c != ""]
            UNIPROT["uniprotac2taxid"][uniprotac] = taxid
            for pdb in pdbs:
                UNIPROT["pdb2uniprot"][pdb].append(uniprotac)
            for pfam in pfams:
                UNIPROT["pfam2uniprot"][pfam].append(uniprotac)


def main(logger):
    # Initiating the parser
    db_api = PsimiSQL(SQL_SEED)
    node_names_to_id = {}


    loadUniprotFile(UNIPROT_DATA_FILE)
    for files in os.listdir('PTM/databases/ELMpred/dssp/LAB/'):
        file_list.append('PTM/databases/ELMpred/dssp/LAB/' + files)
    i=0
    for file in file_list:
        i+=1
        if i == 15000:
            break
        get_match(file)
    get_scores()
    get_protein_id()
    get_taxid()
    get_domain()
    logging.debug('Done creating elm map. Starting adding to DB structure')

    #SELECT elm_prot_id, domain_prot_id, taxid from elm_to_prot
    for m in ELMmaches:
        if len(m.domain_prot_id) > 0 and len(m.elm_prot_id) > 0:
            for m_elm_prot_id in m.elm_prot_id:
                for m_domain_prot_id in m.domain_prot_id:
                    # Creating the node dicts, if the node is already in the db assigning that to the node dict
                    source_dict = insert_or_get_node_dict(m_elm_prot_id, "Uniprot", m.taxid, node_names_to_id, db_api)
                    target_dict = insert_or_get_node_dict(m_domain_prot_id, "Uniprot", m.taxid, node_names_to_id, db_api)

                    # Nodes are inserted to the db if they are not in it yet
                    if 'id' not in source_dict:
                        db_api.insert_node(source_dict)

                    if 'id' not in target_dict:
                        db_api.insert_node(target_dict)

                    edge_dict = {
                        'publication_ids': 'pubmed:26615199',
                        'layer': '2',
                        'source_db': DB_TYPE,  # ontology database citation
                        'interaction_identifiers': None,
                        'confidence_scores': None,  # if available
                        'interaction_detection_method': None,  # probably exp type
                        'interaction_types': 'MI:0190(interaction type)',
                        'first_author': None
                    }

                    db_api.insert_edge(source_dict, target_dict, edge_dict)

    # Saving the to a DB_TYPE.db files
    db_api.save_db_to_file(EXPORT_DB_LOCATION)


if __name__ == '__main__':
    print("Parsing database...")
    main(logger=None)
    print("Parsing database is completed. SQLite database is saved to: " + EXPORT_DB_LOCATION)
