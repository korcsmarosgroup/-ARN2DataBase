"""
  Parses data collected from article: https://www.nature.com/articles/nature09204
"""

# Imports
import csv, logging
from SLKlib.SQLiteDBApi.sqlite_db_api import PsimiSQL

# Constants
SQL_SEED = '../../../../SLKlib/SQLiteDBApi/network-db-seed.sql'
DATA_FILE = 'ARN_chip-ms_Behrends.csv'
EXPORT_DB_LOCATION = '../output/chip_behrends'
DB_TYPE = 'manual curation'

# Initiating logger
logger = logging.getLogger()
handler = logging.FileHandler('../../SLK3.log')
logger.setLevel(logging.DEBUG)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


def main(logger):
    def get_node_a(id, taxid, pathway, alias, topology, psi_mi_to_sql_object):
        """
        This function sets up a node dict and returns it.
        If the node is already in the SQLite database it fetches that node from the db, so it won't be inserted multiple times.
        """

        # Testing if the node is already in the database

        node_dict = psi_mi_to_sql_object.get_node(id, node_tax_id=taxid)

        if not node_dict:
            node_dict = {
                "name": id,
                "tax_id": taxid,
                "alt_accession": None,
                'pathways': pathway,
                "aliases": alias,
                "topology": topology
            }

        return node_dict

    def get_node_b(id, taxid, pathway, alias, topology, psi_mi_to_sql_object):
        """
        This function sets up a node dict and returns it. If the node is already in the SQLite database it fetches that node from the db, so it won't be inserted multiple times.

        """

        # Testing if the node is already in the database
        node_dict = psi_mi_to_sql_object.get_node(id, node_tax_id=taxid)

        if not node_dict:
            node_dict = {
                "name": id,
                "tax_id": taxid,
                "alt_accession": None,
                'pathways': pathway,
                "aliases": alias,
                "topology": topology
            }

        return node_dict

    # Initiating the parser
    db_api = PsimiSQL(SQL_SEED)

    # Parsing data file
    with open(DATA_FILE) as data:
        # Skipping the header
        data.readline()

        for line in data:
            line = line.strip().split(';')
            print(line[17])
            # Taxid
            if line[2] == '9606':
                taxid_source = 'taxid:9606'
            else:
                taxid_source = line[2]
            if line[10] == '9606':
                taxid_target = 'taxid:9606'
            else:
                taxid_target = line[10]

            # Creating the node dicts, if the node is already in the db assigning that to the node dict
            source_dict = get_node_a('uniprot:' + line[1], taxid_source, line[7], line[0], line[4], db_api)
            target_dict = get_node_b('uniprot:' + line[9], taxid_target, line[15], line[8], line[12], db_api)

            # Nodes are inserted to the db if they are not in it yet
            if not 'id' in source_dict:
                db_api.insert_node(source_dict)

            if not 'id' in target_dict:
                db_api.insert_node(target_dict)

            # Mapping layer descriptions to abbreviations
            layer_dict = {
                'Post-translational regulation': '2',
                'Interaction between autophagy proteins': '0',
                'Autophagy regulators': '1'
            }

            # Constructing interaction data line
            int_types = '|'.join(['effect:' + line[19], 'is_directed:' + line[17].split(' ')[1],
                                  'is_direct:' + line[18]])

            edge_dict = {
                'publication_ids': 'pubmed:' + line[20],
                'layer': layer_dict[line[16]],
                'source_db': line[21],
                'interaction_identifiers': None,
                'confidence_scores': line[23],
                'interaction_detection_method': None,
                'interaction_types': int_types,
                'first_author': None
            }

            db_api.insert_edge(source_dict, target_dict, edge_dict)

            # Saving the to a DB_TYPE.db file
        db_api.save_db_to_file(EXPORT_DB_LOCATION)


if __name__ == '__main__':
    print("Parsing database...")
    main(logger=None)
    print("Parsing database is completed. SQLite database is saved to: " + EXPORT_DB_LOCATION)
