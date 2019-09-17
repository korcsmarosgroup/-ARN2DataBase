import sqlite3

conn = sqlite3.connect('all_output/L7sourceDB.db')

with conn:
    c = conn.cursor()

    c.execute("DROP TABLE IF EXISTS edge")
    c.execute("DROP TABLE IF EXISTS node")

    c.execute('''CREATE TABLE edge ('id' INT ,
                                      interactor_a_node_id INT,
                                      interactor_b_node_id INT,
                                      interactor_a_node_name TEXT,
                                      interactor_b_node_name TEXT,
                                      interaction_detection_method TEXT,
                                      first_author TEXT,
                                      publication_ids TEXT,
                                      source_db TEXT,
                                      interaction_identifiers TEXT,
                                      interaction_types TEXT,
                                      confidence_scores TEXT,
                                      layer TEXT)''')
    c.execute('''CREATE TABLE node (
                                    id INT,
                                    name TEXT,
                                    alt_accession TEXT,
                                    tax_id TEXT,
                                    pathways TEXT,
                                    aliases TEXT,
                                    topology TEXT
                                    )''')

    with open('dummy_build_infile.tsv') as edge_infile:
        id_counter = 0
        edge_infile.readline()
        for line in edge_infile:
            id_counter += 1
            line = line.strip().split('\t')
            uniprot_a = 'L7sourceDB:L7sourceDBid' + line[0][-2:]
            uniprot_b = 'L7sourceDB:L7sourceDBid' + line[1][-2:]
            int_det_meth = line[2]
            int_ident = line[3]
            pub = 'pubmed:' + line[4]
            sourcedb = line[5]
            int_type = line[6]
            layer = line[7]

            a_node_id = line[0][-2:]
            b_node_id = line[1][-2:]

            firstauth = None
            score = None

            if layer == '7':
                c.execute("INSERT INTO edge VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                          (id_counter, a_node_id, b_node_id, uniprot_a, uniprot_b, int_det_meth, firstauth, pub, sourcedb, int_ident, int_type,
                          score, layer))
