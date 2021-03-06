"""
Prepare case counts and clade counts data for analysis by subsetting to
specific date range and locations, pruning recent clade counts, and collapsing clades.
"""
import argparse
import pandas as pd
import sys

from datetime import datetime, timedelta

CASES_DTYPES = {
    'location': 'string',
    'cases': 'int64',
}

CLADES_DTYPES = {
    'location': 'string',
    'clade': 'string',
    'sequences': 'int64',
}

# Default cutoff date is today's date
DEFAULT_CUTOFF_DATE = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')


def positive_int(value):
    """
    Custom argparse type function to verify only
    positive integers are provided as arguments
    """
    int_value = int(value)
    if int_value <= 0:
        print(f"ERROR: {int_value} is not a positive integer.", file=sys.stderr)
        sys.exit(1)
    return int_value


if __name__ == '__main__':
    parser = argparse.ArgumentParser(__doc__,
        formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument("--clades", metavar="TSV", required=True,
        help="Path to clade counts TSV with four columns: 'location','clade','date','sequences'")
    parser.add_argument("--cases", metavar="TSV", required=True,
        help="Path to case counts TSV with three columns: 'location','date','cases'")
    parser.add_argument("--max-date", default=DEFAULT_CUTOFF_DATE,
        help="The maximum cutoff for date (inclusive), formatted as 'YYYY-MM-DD'.\n"
             "(default: %(default)s)")
    parser.add_argument("--included-days", type=positive_int,
        help="The number of days (including the cutoff date) to include in analysis.\n"
             "If not provided, all data through the cutoff date will be included.")
    parser.add_argument("--prune-seq-days", type=positive_int,
        help="The number of days (including the cutoff date) to prune sequence counts.\n"
             "This is useful to exclude sequence counts for recent days that are overly enriched for variants.")
    parser.add_argument("--location-min-seq", type=positive_int, default=1,
        help="The mininum number of sequences a location must have within the "
             "days-min-seq to be included in analysis.\n"
             "(default: %(default)s)")
    parser.add_argument("--location-min-seq-days", type=positive_int,
        help="The number of days (counting back from the cutoff date) to use as the date range "
             "for counting the number of sequences per location to determine if a location is included in analysis.\n"
             "If not provided, will count sequences from all dates included in analysis date range.")
    parser.add_argument("--excluded-locations",
        help="File with a list locations to exclude from analysis.")
    parser.add_argument("--clade-min-seq", type=positive_int,
        help="The minimum number of sequences a clades must have to be included as it's own clade.\n"
             "All clades with less than the minimum will be collapsed as 'Other'.")
    parser.add_argument("--clade-min-seq-days", type=positive_int,
        help="The number fo days (counting back from the cutoff date) to use as the date range "
             "for counting the number of sequences per clade to determine if a clade is included as its own clade.\n"
             "If not provided, will count sequences from all dates included in analysis date range.")
    parser.add_argument("--output-clades", required=True,
        help="Path to output TSV file for the prepared clades data.")
    parser.add_argument("--output-cases", required=True,
        help="Path to output TSV file for the prepared cases data.")

    args = parser.parse_args()

    ###########################################################################
    ##################### Rules for subsetting by date ########################
    ###########################################################################
    # Max date to include for analysis
    print(f"Setting max date (inclusive) as {args.max_date!r}.")
    max_date = datetime.strptime(args.max_date, '%Y-%m-%d')

    # The min date is shared between the clades and cases data
    # Set default min_date to minimum date possible so we include all data up to the max date
    min_date = None
    if args.included_days is not None:
        # Calculate the minimum date as *included_days* days before the max date
        # Subtract 1 from days in calculation since we are including the max date
        min_date = max_date - timedelta(days=(args.included_days - 1))
        print(f"Setting min date (inclusive) as {datetime.strftime(min_date, '%Y-%m-%d')!r}.")
    else:
        print("No min date was set, including all dates up to the max date.")

    ###########################################################################
    ################### Rules for subsetting by location ######################
    ###########################################################################
    # Load entire clade counts data since we need to to find all locations
    clades = pd.read_csv(args.clades, sep='\t', parse_dates=['date'], dtype=CLADES_DTYPES)

    # Set the min_date as the default min date for counting sequences per location
    # to count sequences per location over the entire analysis date range
    min_location_seq_date = min_date
    if args.location_min_seq_days is not None:
        print(
            f"Only including locations that have at least {args.location_min_seq} sequence(s)",
            f"in the last {args.location_min_seq_days} days of the analysis date range."
        )
        # Calculate the minimum date for sequences per location as *location_min_seq_days* before the max date
        # Subtract 1 from days in calculation since we are including the max date
        min_location_seq_date = max_date - timedelta(days=(args.location_min_seq_days - 1))
    else:
        print(
            f"Only including locations that have at least {args.location_min_seq} sequence(s)",
            "in the analysis date range."
        )

    # Subset to locations and sequences within the date range from min_location_seq_date to max_date
    # and group by location to get the total number of sequences per location in this date range
    location_and_seqs = clades.loc[
        (clades['date'] >= min_location_seq_date if min_location_seq_date else True) &
        (clades['date'] <= max_date),
        ['location', 'sequences']
    ]
    seqs_per_location = location_and_seqs.groupby(['location'], as_index=False).sum()

    # Get a set of locations that meet the location_min_seq requirement
    locations_with_min_seq = set(seqs_per_location.loc[seqs_per_location['sequences'] >= args.location_min_seq, 'location'])

    # Load manually annotated excluded locations if provided
    excluded_locations = set()
    if args.excluded_locations:
        with open(args.excluded_locations, 'r') as f:
            excluded_locations = {line.rstrip() for line in f}

        print(f"Excluding the following requested locations: {sorted(excluded_locations)}.")

    # Remove excluded-locations from the set of locations to include in analysis
    locations_to_include = locations_with_min_seq - excluded_locations
    print(f"Locations that will be included: {sorted(locations_to_include)}.")

    ###########################################################################
    ###################### Rules for collapsing clades ########################
    ###########################################################################

    # Collapse small clades into "other" if clades-min-seq is provided
    if args.clade_min_seq:
        # Set the min_date as the default min date for counting sequences per clade
        # to count sequences per clade over the entire analysis date range
        min_clades_seq_date = min_date
        if args.clade_min_seq_days is not None:
            print(
                f"Collapsing clades that have less than {args.clade_min_seq} sequence(s)",
                f"in the last {args.clade_min_seq_days} days of the analysis date range into a single 'other' clade."
            )
            # Calculate the minimum date for sequences per clade as *clade_min_seq_days* before the max date
            # Subtract 1 from days in calculation since we are including the max date
            min_clades_seq_date = max_date - timedelta(days=(args.clade_min_seq_days - 1))
        else:
            print(
                f"Collapsing clades that have less than {args.clade_min_seq} sequence(s)",
                "in the analysis date range (inclusive) into a single 'other' clade."
            )

        # Subset to clades and sequences within the date range from min_clades_seq_date to max_date
        # and group by clade to get the total number of sequences per clade in this date range
        clades_and_seqs = clades.loc[
            (clades['date'] >= min_clades_seq_date if min_clades_seq_date else True) &
            (clades['date'] <= max_date),
            ['clade', 'sequences']
        ]
        seqs_per_clade = clades_and_seqs.groupby(['clade'], as_index=False).sum()

        # Get a set of clades that meet the clade_min_seq requirement
        clades_with_min_seq = set(seqs_per_clade.loc[seqs_per_clade['sequences'] >= args.clade_min_seq, 'clade'])

        # Replace clades with 'other' if they do not meet the clade_min_seq requirement
        clades.loc[~clades['clade'].isin(clades_with_min_seq), 'clade'] = 'other'
        # Collapse the 'other' clades of the same location and date
        clades = clades.groupby(['location', 'clade', 'date'], as_index=False).sum()

    ###########################################################################
    ##################### Rules for pruning sequence counts ###################
    ###########################################################################

    # The default max date for clade counts is the max date
    max_clade_date = max_date
    # Set the max date for clade counts to earlier date if prune_seq_days is provided.
    if args.prune_seq_days is not None:
        print(
            f"Pruning clade counts in the last {args.prune_seq_days} day(s)",
            "to exclude recent dates that may be overly enriched for variants."
        )
        # Calculate max clade date as *prune_seq_days* days before the max_date
        max_clade_date = max_date - timedelta(days=(args.prune_seq_days))

    ###########################################################################
    ########################## Subset and output data #########################
    ###########################################################################

    # Subset the clade counts data by date and locations
    clades = clades.loc[
        (clades['date'] >= min_date if min_date else True) &
        (clades['date'] <= max_clade_date) &
        (clades['location'].isin(locations_to_include))
    ]

    print(f"Clades that will be included: {sorted(clades['clade'].unique())}.")

    # Sort clades subset and print to output file
    clades.sort_values(['location', 'clade', 'date']) \
          .to_csv(
              args.output_clades,
              sep='\t',
              index=False,
          )


    # Load entire case counts data
    cases = pd.read_csv(args.cases, sep='\t', parse_dates=['date'], dtype=CASES_DTYPES)
    # Subset the case counts data by date and locations
    cases = cases.loc[
        (cases['date'] >= min_date if min_date else True) &
        (cases['date'] <= max_date) &
        (cases['location'].isin(locations_to_include))
    ]
    # Sort cases subset and print to output file
    cases.sort_values(['location', 'date']) \
         .to_csv(
             args.output_cases,
             sep='\t',
             index=False,
         )
