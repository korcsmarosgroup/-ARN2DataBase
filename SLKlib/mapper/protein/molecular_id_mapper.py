"""
 Maps all nodes of a parsed database to a more universal one, based on the node's molecular type type, by the previously created mapping data sets for each type.
"""

# Impports
import sqlite3
import io, sys

from SLKlib.SQLiteDBApi.sqlite_db_api import PsimiSQL


class MolecularIDMapper:
    def __init__(self, db, layer, PROT_DBname, LNCRNAMAP_DBname):
        """
        :param db: name of the parsed source database
        :param PROT_DBname: if value is not None, database is created in memory
        :argument DICTIONARY_DB_LOCATION: location of the mapping db, output of create_mapping_db
        :argument SQL_SEED_LOCATION
        :argument SOURCE_DB_LOCATION: location of the parsed source database
        :argument DESTINATION_DB_LOCATION: location where the mapped db will be saved
        """

        # Declaring, and assigning constants
        self.DICTIONARY_DB_LOCATION = PROT_DBname
        self.SQL_SEED_LOCATION = '../../SLKlib/SQLiteDBApi/network-db-seed.sql'
        self.SOURCE_DB_TYPE = db
        self.layer = layer
        # The db we want to map
        self.SOURCE_DB_LOCATION = 'all_output/' + db + '.db'
        # Saving location
        self.DESTINATION_DB_LOCATION = '../../SLKlib/mapper/protein/output/' + db + '_mapped.db'
        # Protein map db
        self.DICTIONARY_DB = sqlite3.connect(self.DICTIONARY_DB_LOCATION)
        self.DICTIONARY_DB_CURSOR = self.DICTIONARY_DB.cursor()
        # lncRNA map db
        if self.layer == 'lncRNA' or self.layer == 'miRNA':
            self.LNCRNAMAP_DB_LOCATION = LNCRNAMAP_DBname
            self.LNCRNAMAP_DB = sqlite3.connect(self.LNCRNAMAP_DB_LOCATION)

        self.PROT_DBname = PROT_DBname
        if self.PROT_DBname is not None:
            # Read database to tempfile
            self.con = sqlite3.connect(self.PROT_DBname)
            tempfile = io.StringIO()
            for line in self.con.iterdump():
                tempfile.write('%s\n' % line)
            self.con.close()
            tempfile.seek(0)

            # Create a database in memory and import from tempfile
            self.PROT_DB = sqlite3.connect(":memory:")
            with self.PROT_DB:
                self.PROT_DB.cursor().executescript(tempfile.read())
                self.PROT_DB.cursor().execute("CREATE INDEX map_uniprot ON MAPP(uniprot_ac);")
                self.PROT_DB.cursor().execute("CREATE INDEX uniprotac_id ON UNIPROT_AC(id);")
                self.PROT_DB.cursor().execute("CREATE INDEX taxid ON SPECIES(tax_id);")
                self.PROT_DB.cursor().execute("CREATE INDEX map_foreign ON MAPP(foreign_id);")
        else:
            self.PROT_DB = sqlite3.connect(self.DICTIONARY_DB_LOCATION)
            self.PROT_DB.cursor().execute("CREATE INDEX index_name ON mapp (foreign_id);")

        # For lncRNA and miRNA
        if self.layer == 'lncRNA' or self.layer == 'miRNA':
            self.LNCRNAMAP_DBname = LNCRNAMAP_DBname
            if self.LNCRNAMAP_DBname is not None:
                # Read database to tempfile
                self.con = sqlite3.connect(self.LNCRNAMAP_DBname)
                tempfile = io.StringIO()
                for line in self.con.iterdump():
                    tempfile.write('%s\n' % line)
                self.con.close()
                tempfile.seek(0)

                # Create a database in memory and import from tempfile
                self.LNCRNAMAP_DB = sqlite3.connect(":memory:")
                with self.LNCRNAMAP_DB:
                    self.LNCRNAMAP_DB.cursor().executescript(tempfile.read())
                    self.LNCRNAMAP_DB.cursor().execute("CREATE INDEX index_name ON mapper (orig_ac);")
            else:
                self.LNCRNAMAP_DB = sqlite3.connect(self.LNCRNAMAP_DB_LOCATION)

        self.new_db = PsimiSQL(self.SQL_SEED_LOCATION)
        # iterating through the old_db's nodes
        self.source_db = sqlite3.connect(self.SOURCE_DB_LOCATION)
        self.source_db.row_factory = sqlite3.Row
        self.cur = self.source_db.cursor()

    def add_node(self, old_node_id, old_to_new_node_ids_dict, new_name, new_taxid, new_pathways, new_topo, new_db_api):
        """
        :param old_node_id: node id from the source db's node table
        :param old_to_new_node_ids_dict: A dictionary that contains an old node id as key and new node ids as values
        :param new_name: mapped uniprot ac of the mapped node
        :param new_taxid: taxid
        :param new_pathways: pathway
        :param new_topo: topology
        :param new_db_api: A PsimiSQL object
        """

        new_node_dict = {
            "name": new_name,
            "alt_accession": None, # we don't use it anymore
            "tax_id": new_taxid,
            "pathways": new_pathways,
            "aliases": None,  # we don't use it anymore
            "topology": new_topo
        }

        # inserting the node to the PSI-MI SQLite
        new_db_api.insert_unique_node(new_node_dict)

        # getting the new last row id of the inserted node
        new_node_id = new_node_dict['id']

        # if the node maps to more than one swissprot uniprot id it will be inserted for every swissprot id and
        # this function will be called for every insertion
        if old_node_id not in old_to_new_node_ids_dict:
            old_to_new_node_ids_dict[old_node_id] = new_node_id

    def main(self):
        old_node_ids_dict = {}
        invalid_edge_counter = 0

        # MAPPING NODES
        self.cur.execute("SELECT * FROM node")
        node_counter = 0
        while True:
            # Getting data for each node
            node_row = self.cur.fetchone()
            node_counter += 1
            # Until the last row
            if node_row is None:
                break

            # Getting the old information into a dictionary
            old_node_dict = dict(node_row)

            # For all other databases
            foreign_id = old_node_dict['name'].split(':')[1].strip()
            # Taxid
            taxid = old_node_dict['tax_id'].split(':')[1].split('(')[0]

            # miRNA and lncRNA mapping
            if self.layer == 'lncRNA' or self.layer == 'miRNA':
                with self.LNCRNAMAP_DB:
                    c = self.LNCRNAMAP_DB.cursor()
                    for indiv_id in foreign_id.split(','):
                        indiv_id = indiv_id.replace('"', '').lower()
                        c.execute(
                            '''SELECT mapped_ac FROM MAPPER WHERE '%s' = MAPPER.orig_ac GROUP BY MAPPER.orig_ac'''
                            % indiv_id
                        )
                        firstrow = c.fetchone()
                        if firstrow:
                            m.add_node(node_row['id'], old_node_ids_dict, 'RNACentral:' + firstrow[0],
                                       node_row['tax_id'], node_row['pathways'], node_row['topology'], self.new_db)
                with self.PROT_DB:
                    c2 = self.PROT_DB.cursor()
                    foreign_id = foreign_id.split(".")[0]
                    c2.execute(
                        "SELECT UNIPROT_AC.uniprot_ac, UNIPROT_AC.uniprot_ac_alt_acc FROM UNIPROT_AC "
                        "JOIN MAPP ON MAPP.uniprot_ac=UNIPROT_AC.id "
                        "JOIN SPECIES ON SPECIES.id=UNIPROT_AC.taxon WHERE SPECIES.tax_id='%s'"
                        "AND MAPP.foreign_id='%s' GROUP BY MAPP.foreign_id"
                        % (taxid, foreign_id.lower())
                    )
                    firstrow = c2.fetchone()
                    if firstrow:
                        m.add_node(node_row['id'], old_node_ids_dict, 'Uniprot:' + firstrow[0], node_row['tax_id'],
                                   node_row['pathways'], node_row['topology'], self.new_db)

            # Protein mapping
            else:
                with self.PROT_DB:
                    c = self.PROT_DB.cursor()
                    # Getting uniprot acs for each node and adding the node with new data to the new database
                    foreign_id = foreign_id.split(".")[0]
                    c.execute(
                        "SELECT UNIPROT_AC.uniprot_ac, UNIPROT_AC.uniprot_ac_alt_acc FROM UNIPROT_AC "
                        "JOIN MAPP ON MAPP.uniprot_ac=UNIPROT_AC.id "
                        "JOIN SPECIES ON SPECIES.id=UNIPROT_AC.taxon WHERE SPECIES.tax_id='%s'"
                        "AND MAPP.foreign_id='%s' GROUP BY MAPP.foreign_id"
                        % (taxid, foreign_id.lower())
                    )
                    firstrow = c.fetchone()
                    if firstrow:
                        m.add_node(node_row['id'], old_node_ids_dict, 'Uniprot:' + firstrow[0], node_row['tax_id'],
                                   node_row['pathways'], node_row['topology'], self.new_db)

        # MAPPING EDGES

        # Since we get the old interactor id's from this query we can simply look up ther new id(s) in the old_node_ids dict
        # if both nodes mapped we add them as an edge to the new db

        self.cur.execute("SELECT * from EDGE")
        edge_counter = 0
        while True:
            edge_row = self.cur.fetchone()
            if edge_row is None:
                break
            else:
                edge_counter += 1
                if edge_row['interactor_a_node_id'] in old_node_ids_dict and edge_row['interactor_b_node_id'] in old_node_ids_dict:
                    new_node_id_a = old_node_ids_dict[edge_row['interactor_a_node_id']]
                    new_node_id_b = old_node_ids_dict[edge_row['interactor_b_node_id']]
                    new_node_a_dict = self.new_db.get_node_by_id(new_node_id_a)
                    new_node_b_dict = self.new_db.get_node_by_id(new_node_id_b)

                    new_edge_dict = dict(edge_row)
                    new_edge_dict['interactor_a_node_id'] = new_node_id_a
                    new_edge_dict['interactor_b_node_id'] = new_node_id_b
                    new_edge_dict['source_db'] = edge_row['source_db']

                    # inserting the new node
                    self.new_db.insert_edge(new_node_a_dict, new_node_b_dict, new_edge_dict)
                else:
                    invalid_edge_counter += 1

        # Saving the mapped database
        self.new_db.save_db_to_file(self.DESTINATION_DB_LOCATION)
        print("\nmapping finished for: %s  total edges: %d (unable to map: %d)\n" % (self.SOURCE_DB_TYPE, edge_counter, invalid_edge_counter))

        import slk3_db_validator
        valid = slk3_db_validator.validate_db_file(self.DESTINATION_DB_LOCATION)
        if not valid:
            print("ERROR! invalid db file created by the mapper: " + self.DESTINATION_DB_LOCATION)
            sys.exit(1)

        return self.SOURCE_DB_TYPE, edge_counter, invalid_edge_counter

if __name__ == '__main__':
    for db in DB_LIST:
        m = MolecularIDMapper(db, layer=None)
        m.main()
