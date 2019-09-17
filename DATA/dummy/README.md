Dummy data building

	dummy_source_sql.py, dummy_merger_sql.py, dummy_build_sql.py: scripts that were used to cerate the base of the dummy sql tables, 
		these tables have since been updated manually, DO NOT RUN THESE

	dummy_run_all.py: used for testing downstream parts of the SLK workflow (mapping,mergeing)
		outputs are the same place as the regular create_sources outputs
			mapper output: SLKlib/mapper/protein/output/db_mapped.db
	
	dummy_build_infile.tsv: file containing all edges that are in the final sql of the workflow (all_output/dummy_build.db)
	
	dummy_mergenode_infile.tsv: containing all nodes that are present in the merger sql table (all_output/dummy_merger.db)
	
	all_output
		LxsourceDB.db: (where x is the layer number) SQL database file for all the source databases
		
		dummy_merger_new.db: merger sql database
		dummy_build.db: build sql database
		
		dummy_mapper.db: sql table, protein mapping is done based on this
		dummy_lncrna_maper.db: RNA mapping table
		
		dummy_nodes.json, dummy_edges.json, dummy_attributes.json: final json files, containing the same information as builder
	mapped_output
		mapped database files
		
Nodes that are not in the mapping databases
	L0sourceDB2id28
	L0sourceDB2id31
	therefore edges of these nodes don't map either
		id20 - id28 - layer6
		id28 - id3 - layer0
		id28 - id27 - layer0
		id24 - id31 - layer0
		id29 - id31 - layer0
Node with no edges (should be deleted when running noconn_check.py)
	L0sourceDB2id26
Nodes not in lower layers, but are present in edges of higher layers
	uniprot32 (<- uniprot18) - layer5
	uniprot33 (<- uniprot20) - layer6
	uniprot34 (<- uniprot21) - layer6
	uniprot35 (<- uniprot18) - layer5
Same edge with different attributes (should merge into one)
	uniprot5	uniprot2	intdetmethod4|intdetmethod6	directed	PMID10|PMID11	L0sourceDB|L0sourceDB2	direct	0
	uniprot9	uniprot10	intdetmethod4|intdetmethod6	directed	PMID18|PMID11	L0sourceDB|L0sourceDB2	direct	0
	uniprot24	uniprot30	intdetmethod7|intdetmethod4	is_directed:directed	PMID1	L0sourceDB2	isdirect:direct	0

