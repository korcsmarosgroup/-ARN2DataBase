#!/bin/bash

sql1=${1:-all_output/dummy_merger_new.db}
sql2=${2:-./merger.db}

sqlcommand_node="SELECT name, alt_accession, tax_id, pathways, aliases, topology FROM node ORDER BY name"
sqlcommand_edge="SELECT interactor_a_node_name, interactor_b_node_name, interaction_detection_method, first_author, publication_ids, interaction_types, source_db, interaction_identifiers, confidence_scores, layer FROM edge ORDER BY interactor_a_node_name, interactor_b_node_name, interaction_types"

sqlite3 -separator ';' $sql1 "$sqlcommand_node" > dummy.sql
sqlite3 -separator ';' $sql1 "$sqlcommand_edge" >> dummy.sql

sqlite3 -separator ';' $sql2 "$sqlcommand_node" > actual.sql
sqlite3 -separator ';' $sql2 "$sqlcommand_edge" >> actual.sql

vimdiff actual.sql dummy.sql
rm actual.sql
rm dummy.sql

#vimdiff <(sqlite3 $sql1 "SELECT id, name, alt_accession, tax_id, pathways, aliases, topology FROM node ORDER BY name") <(sqlite3 $sql2 "SELECT id, name, alt_accession, tax_id, pathways, aliases, topology FROM node ORDER BY name")
#vimdiff <(sqlite3 $sql1 "SELECT * FROM edge ORDER BY interactor_a_node_name, interactor_b_node_name") <(sqlite3 $sql2 "SELECT * FROM edge ORDER BY interactor_a_node_name, interactor_b_node_name")