#!/bin/bash

sql1=${1:-all_output/dummy_build.db}
sql2=${2:-./SLK3_layers.db}

sqlcommand_prefix="SELECT layer, interactor_a_node_name, interactor_b_node_name, interaction_detection_method, first_author, publication_ids, interaction_types, source_db, interaction_identifiers, confidence_scores FROM "
sqlcommand_postfix=" ORDER BY layer, interactor_a_node_name, interactor_b_node_name, interaction_types"

sqlcommand_nodes="SELECT name, alt_accession, tax_id, pathways, aliases, topology FROM node ORDER BY name"

sqlite3 -separator ';' $sql1 "${sqlcommand_nodes}"  > dummy.sql
sqlite3 -separator ';' $sql1 "${sqlcommand_prefix} layer0 ${sqlcommand_postfix}"  > dummy.sql
sqlite3 -separator ';' $sql1 "${sqlcommand_prefix} layer1 ${sqlcommand_postfix}" >> dummy.sql
sqlite3 -separator ';' $sql1 "${sqlcommand_prefix} layer2 ${sqlcommand_postfix}" >> dummy.sql
sqlite3 -separator ';' $sql1 "${sqlcommand_prefix} layer3 ${sqlcommand_postfix}" >> dummy.sql
sqlite3 -separator ';' $sql1 "${sqlcommand_prefix} layer5 ${sqlcommand_postfix}" >> dummy.sql
sqlite3 -separator ';' $sql1 "${sqlcommand_prefix} layer6 ${sqlcommand_postfix}" >> dummy.sql
sqlite3 -separator ';' $sql1 "${sqlcommand_prefix} layer7 ${sqlcommand_postfix}" >> dummy.sql

sqlite3 -separator ';' $sql2 "${sqlcommand_nodes}"  > actual.sql
sqlite3 -separator ';' $sql2 "${sqlcommand_prefix} layer0 ${sqlcommand_postfix}" >  actual.sql
sqlite3 -separator ';' $sql2 "${sqlcommand_prefix} layer1 ${sqlcommand_postfix}" >> actual.sql
sqlite3 -separator ';' $sql2 "${sqlcommand_prefix} layer2 ${sqlcommand_postfix}" >> actual.sql
sqlite3 -separator ';' $sql2 "${sqlcommand_prefix} layer3 ${sqlcommand_postfix}" >> actual.sql
sqlite3 -separator ';' $sql2 "${sqlcommand_prefix} layer5 ${sqlcommand_postfix}" >> actual.sql
sqlite3 -separator ';' $sql2 "${sqlcommand_prefix} layer6 ${sqlcommand_postfix}" >> actual.sql
sqlite3 -separator ';' $sql2 "${sqlcommand_prefix} layer7 ${sqlcommand_postfix}" >> actual.sql

vimdiff actual.sql dummy.sql
rm actual.sql
rm dummy.sql

