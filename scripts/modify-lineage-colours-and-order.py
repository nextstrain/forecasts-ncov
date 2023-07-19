import json
import argparse
from pango_aliasor.aliasor import Aliasor
import matplotlib as mpl
import numpy as np

"""
Nextstrain clades, with newest first, and the associated colour scales we want to use
Clade maps taken from https://github.com/nextstrain/forecasts-ncov/blob/70bf78f459a3706dd817ae5f711af3b74887d7b1/viz/src/config.js#L11-L19
NOTE 1: the actual clade name here is never exported, we use it to group lineages
and associate them with a colour. So we may deliberately leave out a clade mapping here
which will group members of that clade with the parent clade, and thus we can use fewer colour
scales.
NOTE 2: Using low start/stop values may result in washed out colours
NOTE 3: following lineages don't get assigned a nextstrain clade (using lineage JSON from 2023-07-17)
XBC.1 , XBC.1.6 , XBC.1.6.3 , XBF ,  XBL 
NOTE 4: The ordered lineages are not cleanly partitioning into clades. For example, scanning
the ordered lineages (L->R) we observe clades 22F -> 23A -> 22F -> 23B -> 22F
"""
CLADES = [
    ['XBB.1.16', '23B', {'name': 'Reds',   'start': 0.7, 'stop': 1  }],
    ['XBB.1.5',  '23A', {'name': 'Reds',   'start': 0.3, 'stop': 0.6}],
    ['XBB',      '22F', {'name': 'YlOrRd', 'start': 0.2, 'stop': 0.5}], # in lineage ordering these 'flank' 23A/23B
    ['BQ.1',     '22E', {'name': 'GnBu',   'start': 0.8, 'stop': 1.0}], 
    ['BA.5',     '22B', {'name': 'GnBu',   'start': 0.5, 'stop': 0.8}], # BA.5 comes after BA.2* in the lineage ordering
    ['BA.2.75',  '22D', {'name': 'GnBu',   'start': 0.3, 'stop': 0.5}],
]
# Define a colour scale for pango lineages which do not have a clade (see NOTE 3 above)
MISSING_COLOUR_SCALE =  {'name': 'Greys',  'start': 0.3, 'stop': 0.6}

def order_lineages(lineages, aliasor):
    """
    Order input lineages by using their full uncompressed lineage & converting to a sortable form
    e.g. BA.5  -> B.1.1.529.5  -> '  B/001/001/529/005'
         BA.16 -> B.1.1.529.16 -> '  B/001/001/529/016'
         so BA.5 is before BA.16
    """
    def _lineage_sortable(lineage):
        if lineage=='other':
            return "ZZZ"
        lin_full = aliasor.uncompress(lineage)
        return "/".join([(f"{x:>3}" if i==0 else f"{int(x):03}") for i,x in enumerate(lin_full.split('.'))])
    return sorted(lineages,key=_lineage_sortable)


def lineage_to_clade(lineage, aliasor, fallback):
    if lineage=='other':
        return lineage
    lineage_full = aliasor.uncompress(lineage)
    for cladeTuple in CLADES:
        comparison_lineage = aliasor.uncompress(cladeTuple[0])
        if lineage_full == comparison_lineage or f"{lineage_full}.".startswith(comparison_lineage):
            return cladeTuple[1]
    return fallback

def colourise(lineages, aliasor):
    """
    Produces an array of arrays associating observed lineages with a colour hex. Example output:
        [
            ['XBB', '#ffffff'],
            ...
        ]
    """
    MISSING = 'missing'
    clades = {lineage: lineage_to_clade(lineage, aliasor, MISSING)
              for lineage in lineages}
    
    colours = []

    for clade in list(set(clades.values())):
        if clade=='other':
            # The viz-app contains a bug whereby missing colours work for some elements (e.g. circles)
            # but not others (e.g. CIs)
            colours.append([clade, '#000'])
            continue

        matching_lineages = [l for l in lineages if clades[l]==clade] # will be ordered
        print(f"{clade:<10}n={len(matching_lineages)} lineages")

        if clade==MISSING:
            details = MISSING_COLOUR_SCALE
        else:
            details = [x[2] for x in CLADES if x[1]==clade][0]
        cmap = mpl.colormaps[details['name']]

        for (lineage, pt) in zip(matching_lineages, np.linspace(details['start'], details['stop'], len(matching_lineages))):
            colours.append([lineage, mpl.colors.to_hex(cmap(pt))])
    return colours


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="lineages JSON")
    parser.add_argument("output", help="(improved) lineages JSON")
    parser.add_argument("--pango-alias", help="[optional] pango alias JSON", default=None)
    args = parser.parse_args()

    aliasor = Aliasor(args.pango_alias)

    with open(args.input, 'r') as fh:
        data = json.load(fh)

    # Sort lineages, but keep the final element in place (the "pivot" variant)
    data['metadata']['variants'] = order_lineages(data['metadata']['variants'][0:-1], aliasor) + [data['metadata']['variants'][-1]]

    print("---- Lineages to associated clades -----")
    for lineage in data['metadata']['variants']:
        print(f"{lineage:<20}{lineage_to_clade(lineage, aliasor, 'MISSING')}")
    print()

    print("---- Generating colours for each observed lineage -----")
    data['metadata']['variantColors'] = colourise(data['metadata']['variants'], aliasor)

    with open(args.output, 'w') as fh:
        json.dump(data, fh, indent=None)