import sqlite3

conn = sqlite3.connect('all_output/dummy_merger_new.db')
old_merge_conn = sqlite3.connect('all_output/dummy_merger.db')

with conn:
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS 'node'")
    c.execute("DROP TABLE IF EXISTS 'edge'")
    c.execute('''CREATE TABLE 'node' ('id' INTEGER PRIMARY KEY,
                                    'name'	TEXT NOT NULL,
                                    'alt_accession'	TEXT,
                                    'tax_id'	INTEGER NOT NULL,
                                    'pathways'	TEXT,
                                    'aliases' TEXT,
                                    'topology' TEXT)''')
    c.execute('''CREATE TABLE `edge` (`id`	INTEGER PRIMARY KEY,
                                      `interactor_a_node_id`	INTEGER NOT NULL,
                                      `interactor_b_node_id`	INTEGER NOT NULL,
                                      `interactor_a_node_name`	TEXT NOT NULL,
                                      `interactor_b_node_name`	TEXT NOT NULL,
                                      `interaction_detection_method`	TEXT,
                                      `first_author`	TEXT,
                                      `publication_ids`	TEXT NOT NULL,
                                      `interaction_types`	TEXT,
                                      `source_db`	TEXT NOT NULL,
                                      `interaction_identifiers`	TEXT,
                                      `confidence_scores`	TEXT,
                                      `layer` INTEGER NOT NULL)''')

with old_merge_conn:
    c2 = old_merge_conn.cursor()
    c2.execute("SELECT * FROM node")
    while True:
        row = c2.fetchone()
        if row is None:
            break
        else:
            with conn:
                c.execute("INSERT INTO node VALUES (?,?,?,?,?,?,?)", row)

with old_merge_conn:
    c2 = old_merge_conn.cursor()
    c2.execute("SELECT * FROM edge")
    while True:
        row = c2.fetchone()
        if row is None:
            break
        else:
            with conn:
                c.execute("INSERT INTO edge VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)", row)
