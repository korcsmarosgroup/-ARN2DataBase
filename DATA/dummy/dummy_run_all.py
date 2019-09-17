"""
Runs all SLK3 scripts
"""
# Imports
import os

os.environ['SIGNALINK_MAPPER_LOCATION'] = 'all_output/dummy_mapper.db'
os.environ['SIGNALINK_JSON_MAPPER_FILE'] = 'all_output/dummy_uniprot_id_mapping.json'


from collections import OrderedDict as OD

from SLKlib.mapper.protein import molecular_id_mapper as mol
from SLKlib.merger import merge_layer
from SLKlib import build_new as builder
from SLKlib import noconn_check as noconn
from SLKlib import sort_data as sorter

DB_DICT = OD([
    ('SLK_Core', ['L0sourceDB', 'L0sourceDB2']),
    ('layer1', ['L1sourceDB']),
    ('PTM', ['L2sourceDB']),
    ('ATG_Reg', ['L3sourceDB']),
    ('miRNA', ['L5sourceDB']),
    ('TF', ['L6sourceDB']),
    ('lncRNA', ['L7sourceDB']),
])
# Mapping
for layer in DB_DICT.keys():
    for mol.db in DB_DICT[layer]:
        mol.m = mol.MolecularIDMapper(mol.db, PROT_DBname='all_output/dummy_mapper.db',
                                      LNCRNAMAP_DBname='all_output/dummy_lncrna_mapper.db',
                                      layer=layer)
        mol.m.main()

# Merge layers
merge_layer.SQL_SEED_LOCATION = '../../SLKlib/SQLiteDBApi/network-db-seed.sql'
merge_layer.DESTINATION = 'merger.db'
path = '../../SLKlib/mapper/protein/output/'
dblist = []
for layer in DB_DICT.keys():
    for db in DB_DICT[layer]:
        dblist.append(path + db + '_mapped.db')
merge_layer.SOURCE_DB_FILE_LIST = dblist
merge_layer.main(log=None)

# Deleting nodes from merger that have no connections
noconn.main(logger=None, merger_path='merger.db')

# Building all layers
builder.main(log=None, path='merger.db')

# Sorting data into the final json format
sorter.mapper_location = os.environ['SIGNALINK_MAPPER_LOCATION']
sorter.json_mapper_file = os.environ['SIGNALINK_JSON_MAPPER_FILE']
sorter.logger_output_location = 'SLK3.log'
sorter.get_node_data(builder_location='SLK3_layers.db')
sorter.get_edge_data(builder_location='SLK3_layers.db')
sorter.get_attribute_data(merger_location='merger.db', builder_location='SLK3_layers.db')
