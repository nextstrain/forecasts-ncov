"""
Prepare a submission for a single model to the variant hub.
"""
import argparse


if __name__ == '__main__':
    parser = argparse.ArgumentParser(__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--hub-tasks", required=True, help="JSON of hub tasks with list of target dates, clades, and locations to estimate frequencies for")
    parser.add_argument("--model", required=True, help="JSON representing main model outputs from evofr")
    parser.add_argument("--posterior", required=True, help="JSON of posterior samples corresponding to the given main model's parameters")
    parser.add_argument("--state-to-abbreviation-map", required=True, help="TSV mapping full US state and territory names to two-letter abbreviations")
    parser.add_argument("--output", required=True, help="parquet file representing posterior samples of frequencies for the target dates, clades, and locations")

    args = parser.parse_args()
