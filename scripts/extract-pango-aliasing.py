import argparse
import csv
import json
import re
from augur.utils import json_to_tree, annotate_parents_for_tree

def collect_args():
    parser = argparse.ArgumentParser(description = "Extract clade and lineage tip attributes")
    parser.add_argument('--json', required=True, type=str, help="input JSON file")
    parser.add_argument('--output', required=True, type=str, help="output TSV file that maps Nextstrain clade, Pango lineage and dealiased Pango lineage")
    return parser.parse_args()

if __name__=="__main__":
    params = collect_args()

    json_fh = open(params.json, "r")
    json_dict = json.load(json_fh)
    tree = json_to_tree(json_dict)

    with open(params.output, "w") as outputfile:
        out = csv.writer(outputfile, delimiter = '\t')
        out.writerow(("seqName", "clade", "Nextclade_pango", "partiallyAliased"))

        data = []
        for n in tree.find_clades(order="postorder"):
            node_elements = {}
            node_elements["name"] = n.name

            if hasattr(n, 'node_attrs'):
                for attr in ['clade_membership', 'Nextclade_pango', 'partiallyAliased']:
                    node_elements[attr] = n.node_attrs.get(attr, {}).get("value", "?")

            if re.match(r'^[A-Z]+(\.[0-9]+)*$', node_elements["name"]):
                out.writerow((node_elements["name"],
                    node_elements["clade_membership"],
                    node_elements["Nextclade_pango"],
                    node_elements["partiallyAliased"]))
