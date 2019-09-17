/dummy
	containing dummy data files
	
/workflow
	files and modules completing the data importing from source DBs
	to unified SQL structure
	
	/layerx/databases
		containing a folder for each of the imported databases
			script.py: script that is called during the workflow execution 
			(when running create_sources.py)
			/files
				directory containing input files of importing scripts
	/all_output
		destination directory of output SQL files of importing scripts (databasename.db)
	
	download.py	
		input: sources.json
		automated download of available imported databases from their website adresses
		output: layerx/databases/database/files
	create_sources.py	
		runs all of the importing scripts for each databases, creates SQL tables
		output: all_output
	build_slk3.py
		runs upstream parts of the workflow (mapping, mergeing, building)
		
/prediction
	predicted data workflow
	