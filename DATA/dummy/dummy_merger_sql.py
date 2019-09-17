import sqlite3

conn = sqlite3.connect('dummy_merger.db')

with conn:
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS edge")
    c.execute("DROP TABLE IF EXISTS node")

    c.execute('''CREATE TABLE edge (interactor_a_node_id INT,
                                    interactor_b_node_id INT,
                                    interactor_a_node_name TEXT,
                                    interactor_b_node_name TEXT,
                                    interaction_detection_method TEXT,
                                    first_author TEXT,
                                    publication_ids TEXT,
                                    interaction_identifiers TEXT,
                                    source_db TEXT,
                                    interaction_types TEXT,
                                    confidence_scores TEXT,
                                    layer TEXT) ''')
    c.execute('''CREATE TABLE node (id INT,
                                    name TEXT,
                                    alt_accession TEXT,
                                    tax_id TEXT,
                                    pathways TEXT,
                                    aliases TEXT,
                                    topology TEXT)''')

    with open('dummy_build_infile.tsv') as edge_infile:
        edge_infile.readline()
        a_node_id = 0
        b_node_id = 0
        for line in edge_infile:
            a_node_id += 1
            b_node_id += 1
            line = line.strip().split('\t')
            uniprot_a = 'uniprot:' + line[0]
            uniprot_b = 'uniprot:' + line[1]
            int_det_meth = line[2]
            int_ident = line[3]
            pub = 'pubmed:' + line[4]
            sourcedb = line[5]
            int_type = line[6]
            layer = line[7]

            firstauth = None
            score = None

            c.execute("INSERT INTO edge VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                      (a_node_id, b_node_id, uniprot_a, uniprot_b, int_det_meth, firstauth, pub, int_ident, sourcedb,
                       int_type, score, layer))

    with open('dummy_mergenode_infile.tsv') as node_infile:
        node_infile.readline()
        id_counter = 0
        for line in node_infile:
            id_counter += 1
            line = line.strip().split('\t')
            name = 'uniprot:' + line[0]
            alt_acc = line[1]
            tax_id = 'taxid:' + line[2]
            if len(line) > 3:
                pathway = 'pathway:' + line[3]
            else:
                pathway = None

            alias = None
            topol = None

            c.execute("INSERT INTO node VALUES (?,?,?,?,?,?,?)",
                      (id_counter, name, alt_acc, tax_id, pathway, alias, topol))

