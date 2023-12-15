import json
import argparse
from pango_aliasor.aliasor import Aliasor
import matplotlib as mpl
import numpy as np
import colorsys


# Color for clades that lack clade definition, but we don't want to group with 'other'
DEFAULT_CLADE_COLOR = '#474747'


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


def lineage_to_clade(lineage, aliasor, fallback, clade_definitions):
    lineage_full = aliasor.uncompress(lineage)
    for clade_data in clade_definitions:
        if clade_data['clade']=='other':
            continue
        comparison_lineage = aliasor.uncompress(clade_data['defining_lineage'])
        if lineage_full == comparison_lineage or lineage_full.startswith(comparison_lineage + "."):
            return clade_data['clade']
    return fallback

def clade_colors(variants, clade_definitions):
    colors = {c['clade']: c['color'] for c in clade_definitions}
    missing = set()
    defs = []
    for v in variants:
        try:
            defs.append([v, colors[v]])
        except KeyError:
            if v!='other':
                missing.add(v)
                defs.append([v, DEFAULT_CLADE_COLOR])

    # TODO: Emit this to output file so it can be sent thru Slack notifications
    if len(missing) > 0:
        print(
            f"Missing definitions for the following clades: {', '.join(missing)}.",
            f"They have been assigned the default color {DEFAULT_CLADE_COLOR!r}"
        )

    return defs

def clade_display_names(variants, clade_definitions):
    display_names = {c['clade']: c['display_name'] for c in clade_definitions}
    return [[name, display_names[name] if name in display_names else name]
            for name in variants]

def colour_range(anchor, n):
    """
    Create a range of `n` colours centred around the provided `anchor`.
    This currently involves simple manipulations in HLS space, but
    the outputs aren't going to be as good as they could be if we did it in
    a perceptually uniform space (e.g lab space). For the purposes of this viz
    I don't think it's a dealbreaker, and in our current setup it's hard to use
    python libraries which aren't already available in our various runtimes.
    """
    anchor_rgb = tuple(int(anchor.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
    anchor_hls = colorsys.rgb_to_hls(*anchor_rgb)
    hrange = np.linspace(anchor_hls[0]*0.85, anchor_hls[0]*1.25, n)
    lrange = np.linspace(anchor_hls[1]*1.2, anchor_hls[1], n)
    srange = np.linspace(anchor_hls[2]*0.7, anchor_hls[2]*1.1, n)
    rgb_range = [colorsys.hls_to_rgb(*hls) for hls in zip(hrange, lrange, srange)]
    def clamp(x):
        return int(max(0, min(x, 255)))
    return [f"#{clamp(rgb[0]):02x}{clamp(rgb[1]):02x}{clamp(rgb[2]):02x}" for rgb in rgb_range]

def colourise(lineages, aliasor, clade_definitions):
    """
    Produces an array of arrays associating observed lineages with a colour hex. Example output:
        [
            ['XBB', '#ffffff'],
            ...
        ]
    """
    clades = {lineage: lineage_to_clade(lineage, aliasor, 'other', clade_definitions)
              for lineage in lineages}

    colours = []

    for clade in list(set(clades.values())):
        matching_lineages = [l for l in lineages if clades[l]==clade] # will be ordered
        print(f"{clade:<10}n={len(matching_lineages)} lineages")
        color_hex = [x['color'] for x in clade_definitions if x['clade']==clade][0]
        for pair in zip(matching_lineages, colour_range(color_hex, len(matching_lineages))):
            colours.append(pair)
    return colours


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, metavar="JSON")
    parser.add_argument("--output", required=True, metavar="JSON")
    parser.add_argument("--variant-classification", required=True, help="Data will be modified for 'nextstrain_clades' or 'pango_lineages'")
    parser.add_argument("--config", required=True, metavar="JSON string", help="clade definitions")
    parser.add_argument("--pango-alias", help="[optional] pango alias JSON", default=None)
    args = parser.parse_args()

    with open(args.input, 'r') as fh:
        data = json.load(fh)
    clade_definitions = json.loads(args.config)

    if (args.variant_classification=='nextstrain_clades'):
        data['metadata']['variantColors'] = clade_colors(data['metadata']['variants'], clade_definitions)
        data['metadata']['variantDisplayNames'] = clade_display_names(data['metadata']['variants'], clade_definitions)

    elif (args.variant_classification=='pango_lineages'):
        aliasor = Aliasor(args.pango_alias)

        # Sort lineages, but keep the final element in place (the "pivot" variant)
        data['metadata']['variants'] = order_lineages(data['metadata']['variants'][0:-1], aliasor) + [data['metadata']['variants'][-1]]

        print("---- Lineages to associated clades -----")
        for lineage in data['metadata']['variants']:
            print(f"{lineage:<20}{lineage_to_clade(lineage, aliasor, 'other', clade_definitions)}")
        print()

        print("---- Generating colours for each observed lineage -----")
        data['metadata']['variantColors'] = colourise(data['metadata']['variants'], aliasor, clade_definitions)

    else:
        print(f"Variant classification of {args.variant_classification}: no post-processing of JSON")

    with open(args.output, 'w') as fh:
        json.dump(data, fh, indent=None)
