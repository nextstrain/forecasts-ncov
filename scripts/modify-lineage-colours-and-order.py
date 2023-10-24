import json
import argparse
from pango_aliasor.aliasor import Aliasor
import matplotlib as mpl
import numpy as np

"""
A mapping between pango lineages, nextstrain clades, and colour ramps to use for child lineages 
of these clades. This allows each individual lineage to have its own colour whilst being able
to visually associate them back to their nextstrain clade.

NOTES:
* The colours for the clades model runs are defined in `../viz/src/config.js`
* Summary of available colour ramps: <https://matplotlib.org/stable/gallery/color/colormap_reference.html>
* Lineages are ordered (in the legend & for the GA estimates) alphabetically via their full
  pango name. This doesn't map nicely onto nextstrain clade definitions, which is why an individual
  colour scale defined here may appear in multiple parts of the graph.
* Using low start/stop values may result in washed out colours
* Lineages which are not a descendant of a clade-defining lineage will be greyscale.
"""
CLADES = [
    ['EG.5.1',   '23F', {'name': 'YlOrRd',   'start': 0.7, 'stop': 0.8  }],
    ['XBB.2.3',  '23E', {'name': 'YlOrRd',   'start': 0.5, 'stop': 0.6  }],
    ['XBB.1.9',  '23D', {'name': 'YlOrRd',   'start': 0.2, 'stop': 0.4  }],
    ['CH.1.1',   '23C', {'name': 'Greens',   'start': 0.4, 'stop': 0.7  }],
    ['XBB.1.16', '23B', {'name': 'YlGnBu',   'start': 0.3, 'stop': 0.5  }],
    ['XBB',      '22F', {'name': 'Blues',    'start': 0.4, 'stop': 0.8  }],

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