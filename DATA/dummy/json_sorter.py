import json

def sort(nodes_json, edge_json, attribute_json):
    jsondata = json.loads(open(nodes_json).read())
    with open(nodes_json + '_sorted.json', 'w') as outfile2:
        jsondata.sort(key=lambda x: x['name'])
        json.dump(jsondata, outfile2, indent=4, sort_keys=True)

    jsondata = json.loads(open(edge_json).read())
    with open(edge_json + '_sorted.json', 'w') as outfile2:
        jsondata.sort(key=lambda x: "%s.%s.%s" % (str(x['layer'][0]['value']), x['source'], x['target']))
        json.dump(jsondata, outfile2, indent=4, sort_keys=True)

    jsondata = json.loads(open(attribute_json).read())
    with open(attribute_json + '_sorted.json', 'w') as outfile2:
        jsondata.sort(key=lambda x: x['key'])
        json.dump(jsondata, outfile2, indent=4, sort_keys=True)


sort('all_output/dummy_nodes.json', 'all_output/dummy_edges.json', 'all_output/dummy_attributes.json')
sort('nodes.json', 'edges.json', 'attributes.json')

