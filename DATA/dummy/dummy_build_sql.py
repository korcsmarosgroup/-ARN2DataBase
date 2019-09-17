import sqlite3

conn = sqlite3.connect('dummy_build.db')

with conn:
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS SLK_Core")
    c.execute("DROP TABLE IF EXISTS layer1")
    c.execute("DROP TABLE IF EXISTS PTM")
    c.execute("DROP TABLE IF EXISTS ATG_Reg")
    c.execute("DROP TABLE IF EXISTS miRNA")
    c.execute("DROP TABLE IF EXISTS TF")
    c.execute("DROP TABLE IF EXISTS lncRNA")

    c.execute('''CREATE TABLE SLK_Core (
                                      interactor_a_node_id INT,
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
    c.execute('''CREATE TABLE layer1 (
                                      interactor_a_node_id INT,
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
                                      layer TEXT)
                ''')
    c.execute('''CREATE TABLE PTM (
                                      interactor_a_node_id INT,
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
                                      layer TEXT)''')
    c.execute('''CREATE TABLE ATG_Reg (
                                      interactor_a_node_id INT,
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
                                      layer TEXT)''')
    c.execute('''CREATE TABLE miRNA (
                                      interactor_a_node_id INT,
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
                                      layer TEXT)''')
    c.execute('''CREATE TABLE TF (
                                      interactor_a_node_id INT,
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
                                      layer TEXT)''')
    c.execute('''CREATE TABLE lncRNA (
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

    a_node_id = 0
    b_node_id = 0
    with open('dummy_build_infile.tsv') as infile:
        infile.readline()
        for line in infile:
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
            score= None

            if layer == '0':
                c.execute("INSERT INTO SLK_Core VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                          (a_node_id, b_node_id, uniprot_a, uniprot_b, int_det_meth, firstauth, pub, int_ident, sourcedb, int_type, score, layer))
            elif layer == '1':
                c.execute("INSERT INTO layer1 VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                          (a_node_id, b_node_id, uniprot_a, uniprot_b, int_det_meth, firstauth, pub, int_ident, sourcedb, int_type, score, layer))
            elif layer == '2':
                c.execute("INSERT INTO PTM VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                          (a_node_id, b_node_id, uniprot_a, uniprot_b, int_det_meth, firstauth, pub, int_ident, sourcedb, int_type, score, layer))
            elif layer == '3':
                c.execute("INSERT INTO ATG_Reg VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                          (a_node_id, b_node_id, uniprot_a, uniprot_b, int_det_meth, firstauth, pub, int_ident, sourcedb, int_type, score, layer))
            elif layer == '5':
                c.execute("INSERT INTO miRNA VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                          (a_node_id, b_node_id, uniprot_a, uniprot_b, int_det_meth, firstauth, pub, int_ident, sourcedb, int_type, score, layer))
            elif layer == '6':
                c.execute("INSERT INTO TF VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                          (a_node_id, b_node_id, uniprot_a, uniprot_b, int_det_meth, firstauth, pub, int_ident, sourcedb, int_type, score, layer))
            elif layer == '7':
                c.execute("INSERT INTO lncRNA VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                          (a_node_id, b_node_id, uniprot_a, uniprot_b, int_det_meth, firstauth, pub, int_ident, sourcedb, int_type, score, layer))