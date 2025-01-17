"""
  Parsing Autophagy core data from ARN1
"""

# Imports
from SLKlib.SQLiteDBApi.sqlite_db_api import PsimiSQL
import sqlite3, os

# Defining constants
SQL_SEED = '../../../../../SLKlib/SQLiteDBApi/network-db-seed.sql'
DATA_FILE = 'files/Layer0.csv'
DB_DESTINATION = '../../../all_output/ARN1Core.db'


def get_node_a(aid, taxid, name, psi_mi_to_sql_object):
    """
    This function sets up a node dict and returns it. If the node is already in the SQLite database it fetches that node from the db, so it won't be inserted multiple times.
    """

    # Testing if the node is already in the database
    node_dict = psi_mi_to_sql_object.get_node(aid, node_tax_id=taxid)

    if not node_dict:
        node_dict = {
            "name": aid,
            "tax_id": taxid,
            "alt_accession": name,
            'pathways': None,
            "aliases": None,
            "topology": None
        }

    return node_dict


def get_node_b(bid, taxid, name, psi_mi_to_sql_object):
    """
    This function sets up a node dict and returns it. If the node is already in the SQLite database it fetches that node from the db, so it won't be inserted multiple times.
    """

    # Testing if the node is already in the database
    node_dict = psi_mi_to_sql_object.get_node(bid, node_tax_id=taxid)

    if not node_dict:
        node_dict = {
            "name": bid,
            "tax_id": taxid,
            "alt_accession": name,
            'pathways': None,
            "aliases": None,
            "topology": None
        }

    return node_dict


def main(logger):
    # Initiating the parser
    db_api = PsimiSQL(SQL_SEED)
    dest_conn = sqlite3.connect(DB_DESTINATION)

    # Parsing file
    with open(DATA_FILE, encoding='ISO-8859-1') as data:
        data.readline()
        for line in data:
            line = line.strip().split(',')

            source_uniprot = line[2]
            target_uniprot = line[3]

            source_genename = line[0]
            target_genename = line[1]
            # Creating the node dicts, if the node is already in the db assigning that to the node dict
            source_dict = get_node_a('Uniprot:' + source_uniprot, 'taxid:9606', source_genename, db_api)
            target_dict = get_node_b('Uniprot:' + target_uniprot, 'taxid:9606', target_genename, db_api)

            # Nodes are inserted to the db if they are not in it yet
            if 'id' not in source_dict:
                db_api.insert_node(source_dict)

            if 'id' not in target_dict:
                db_api.insert_node(target_dict)

            # Layer mapping
            layer_map_dict = {
                'Interaction between autophagy proteins': 0
            }
            # Effect mapping
            effect_map_dict = {
                'unknown': 'unknown',
                "stimulation": 'MI:0624(stimulation)',

            }
            # Directedness mapping
            direct_map_dict = {
                "direct": "MI:0407(directed)",
                "indirect": "MI:2246(indirect)",
            }
            # Setting up identifiers
            directness = direct_map_dict[line[5]]
            effect = effect_map_dict[line[6]]
            # Assembling line
            ident = ('effect:' + effect + '|is_direct:' + directness)

            # Publications
            pubs = '|pubmed:'.join(line[7].split('|'))

            # Sourcedb
            sourcedb = line[8].split('(')[0].replace('"','')

            source_map = {
                'BioGRID': 'TheBiogrid',
                'Behrends et Al. 2010': 'Behrends'
            }

            if sourcedb in source_map:
                source = source_map[sourcedb]
            else:
                source = sourcedb

            edge_dict = {
                'publication_ids': 'pubmed:' + pubs,
                'layer': layer_map_dict[line[4]],
                'source_db': source,
                'interaction_identifiers': ident,
                'confidence_scores': None,
                'interaction_detection_method': None,
                'interaction_types': None,
                'first_author': None
            }

            db_api.insert_edge(source_dict, target_dict, edge_dict)

            # Saving the to a DB_TYPE.db file
        db_api.save_db_to_file(DB_DESTINATION)


# if __name__ == '__main__':
#     main(None)

