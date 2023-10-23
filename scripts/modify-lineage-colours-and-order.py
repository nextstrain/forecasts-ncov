import json
import argparse
from pango_aliasor.aliasor import Aliasor
import matplotlib as mpl
import numpy as np

"""
A mapping between pango lineages, nextstrain clades, and colour ramps to use for child lineages 
of these clades. This allows each individual lineage to have its own colour whilst being able
to visually associate them back to their nextstrain clade.

The order in the list must be heirarchical w.r.t pango lineages, i.e. XBB.1.9 must appear _before_ XBB

Keys:
    - defining_lineage: the pango lineage which defines the nextstrain clade
    - clade: the nextstrain clade
    - display_name: clade name to use when visualising the clades model outputs
    - color: the hex value to use for the clade (in the clades model output)
    - cmap: colourmap details to construct colours for the lineages associated with the clade

NOTES:
    * Summary of available colour ramps: <https://matplotlib.org/stable/gallery/color/colormap_reference.html>
    * Lineages are ordered (in the legend & for the GA estimates) alphabetically via their full
    pango name. This doesn't map nicely onto nextstrain clade definitions, which is why an individual
    colour scale defined here may appear in multiple parts of the graph.
    * Using low start/stop values may result in washed out colours
    * Lineages which are not a descendant of a clade-defining lineage will be greyscale.
"""
CLADES = [
    {'defining_lineage': 'EG.5.1',   'clade': '23F', 'display_name': "23F (EG.5.1)",
        'color': '#DC2F24', 'cmap': {'name': 'YlOrRd',   'start': 0.7, 'stop': 0.8  }},
    {'defining_lineage': 'XBB.2.3',  'clade': '23E', 'display_name': "23E (XBB.2.3)",
        'color': '#E68133', 'cmap': {'name': 'YlOrRd',   'start': 0.5, 'stop': 0.6  }},
    {'defining_lineage': 'XBB.1.9',  'clade': '23D', 'display_name': "23D (XBB.1.9)",
        'color': '#D4B13F', 'cmap': {'name': 'YlOrRd',   'start': 0.2, 'stop': 0.4  }},
    {'defining_lineage': 'CH.1.1',   'clade': '23C', 'display_name': "23C (CH.1.1)",
        'color': '#A6BE55', 'cmap': {'name': 'Greens',   'start': 0.4, 'stop': 0.7  }},
    {'defining_lineage': 'XBB.1.16', 'clade': '23B', 'display_name': "23B (XBB.1.16)",
        'color': '#75B681', 'cmap': {'name': 'YlGnBu',   'start': 0.3, 'stop': 0.5  }},
    {'defining_lineage': 'XBB',      'clade': '22F', 'display_name': "22F (XBB)",
        'color': '#3F63CF', 'cmap': {'name': 'Blues',    'start': 0.4, 'stop': 0.8  }},
    {'defining_lineage': 'XBB.1.5',  'clade': '23A', 'display_name': "23A (XBB.1.5)",
        'color': '#529AB6', 'cmap': {'name': 'cool',    'start': 0.1, 'stop': 0.2  }},
    {'defining_lineage': None,      'clade': 'other', 'display_name': "other",
        'color': '#777777', 'cmap': {'name': 'Greys',  'start': 0.5, 'stop': 0.8}},
]

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
    lineage_full = aliasor.uncompress(lineage)
    for clade_data in CLADES:
        if clade_data['clade']=='other':
            continue
        comparison_lineage = aliasor.uncompress(clade_data['defining_lineage'])
        if lineage_full == comparison_lineage or f"{lineage_full}.".startswith(comparison_lineage):
            return clade_data['clade']
    return fallback

def clade_colors(variants):
    colors = {c['clade']: c['color'] for c in CLADES}
    missing = set()
    defs = []
    for v in variants:
        try:
            defs.append([v, colors[v]])
        except KeyError:
            if v!='other':
                missing.add(v)
    assert len(missing) == 0, f"Missing definitions for the following clades: {', '.join(missing)}"
    return defs

def clade_display_names(variants):
    display_names = {c['clade']: c['display_name'] for c in CLADES}
    return [[name, display_names[name] if name in display_names else name]
            for name in variants]

def colourise(lineages, aliasor):
    """
    Produces an array of arrays associating observed lineages with a colour hex. Example output:
        [
            ['XBB', '#ffffff'],
            ...
        ]
    """
    clades = {lineage: lineage_to_clade(lineage, aliasor, 'other')
              for lineage in lineages}
    
    colours = []

    for clade in list(set(clades.values())):
        matching_lineages = [l for l in lineages if clades[l]==clade] # will be ordered
        print(f"{clade:<10}n={len(matching_lineages)} lineages")
        details = [x['cmap'] for x in CLADES if x['clade']==clade][0]
        cmap = mpl.colormaps[details['name']]

        for (lineage, pt) in zip(matching_lineages, np.linspace(details['start'], details['stop'], len(matching_lineages))):
            colours.append([lineage, mpl.colors.to_hex(cmap(pt))])
    return colours


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, metavar="JSON")
    parser.add_argument("--output", required=True, metavar="JSON")
    parser.add_argument("--variant-classification", required=True, help="Data will be modified for 'nextstrain_clades' or 'pango_lineages'")
    parser.add_argument("--pango-alias", help="[optional] pango alias JSON", default=None)
    args = parser.parse_args()

    with open(args.input, 'r') as fh:
        data = json.load(fh)

    if (args.variant_classification=='nextstrain_clades'):
        data['metadata']['variantColors'] = clade_colors(data['metadata']['variants']) # will exit if not all variants are defined
        data['metadata']['variantDisplayNames'] = clade_display_names(data['metadata']['variants'])

    elif (args.variant_classification=='pango_lineages'):
        aliasor = Aliasor(args.pango_alias)

        # Sort lineages, but keep the final element in place (the "pivot" variant)
        data['metadata']['variants'] = order_lineages(data['metadata']['variants'][0:-1], aliasor) + [data['metadata']['variants'][-1]]

        print("---- Lineages to associated clades -----")
        for lineage in data['metadata']['variants']:
            print(f"{lineage:<20}{lineage_to_clade(lineage, aliasor, 'other')}")
        print()

        print("---- Generating colours for each observed lineage -----")
        data['metadata']['variantColors'] = colourise(data['metadata']['variants'], aliasor)

    else:
        print(f"Variant classification of {args.variant_classification}: no post-processing of JSON")

    with open(args.output, 'w') as fh:
        json.dump(data, fh, indent=None)