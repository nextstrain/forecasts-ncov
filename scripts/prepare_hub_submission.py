"""
Prepare a submission for a single model to the variant hub.
"""
import argparse
import json
import numpy as np
import pandas as pd
import sys

MAX_PRECISION = 6

if __name__ == '__main__':
    parser = argparse.ArgumentParser(__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--hub-tasks", required=True, help="JSON of hub tasks with list of target dates, clades, and locations to estimate frequencies for")
    parser.add_argument("--model", required=True, help="JSON representing main model outputs from evofr")
    parser.add_argument("--posterior", required=True, help="JSON of posterior samples corresponding to the given main model's parameters")
    parser.add_argument("--state-to-abbreviation-map", required=True, help="CSV mapping full US state and territory names to two-letter abbreviations")
    parser.add_argument("--output", required=True, help="parquet file representing posterior samples of frequencies for the target dates, clades, and locations")

    args = parser.parse_args()

    # Determine expected dates, clades, and locations for the current hub task
    # and the number of posterior samples we need for the output.
    print("Loading tasks")
    with open(args.hub_tasks, "r", encoding="utf-8") as fh:
        tasks = json.load(fh)

    # Rounds appear in an ordered list such that the last item is the latest
    # round.
    latest_round = tasks["rounds"][-1]["model_tasks"][0]
    latest_tasks = latest_round["task_ids"]
    nowcast_date = latest_tasks["nowcast_date"]["required"][0]
    print(f"Nowcast from {nowcast_date}")
    target_dates = latest_tasks["target_date"]["optional"]
    print(f"Target dates: {len(target_dates)} spanning {target_dates[0]} to {target_dates[-1]}")
    locations = latest_tasks["location"]["optional"]
    print(f"Locations: {len(locations)}")
    clades = latest_tasks["clade"]["required"]
    print(f"Required clades: {len(clades)} including {clades}")
    min_samples = latest_round["output_type"]["sample"]["output_type_id_params"]["min_samples_per_task"]
    print(f"Extract {min_samples} samples from the posterior")
    print()

    # Extract the list of dates, clades, and locations estimated from the main model JSON.
    print("Loading model")
    with open(args.model, "r", encoding="utf-8") as fh:
        model = json.load(fh)

    model_dates = model["metadata"]["dates"]
    model_forecast_dates = model["metadata"]["forecast_dates"]
    model_locations = [
        location
        for location in model["metadata"]["location"]
        if location != "hierarchical"
    ]
    model_clades = model["metadata"]["variants"]

    print(f"Model nowcast dates: {len(model_dates)} spanning from {model_dates[0]} to {model_dates[-1]}")
    print(f"Model forecast dates: {len(model_forecast_dates)} spanning from {model_forecast_dates[0]} to {model_forecast_dates[-1]}")
    print(f"Model locations: {len(model_locations)}")
    print(f"Model clades: {len(model_clades)} including {model_clades}")

    # Map required clades to modeled clades.
    # Any required clades that aren't modeled should produce an error.
    # Any modeled clades that aren't required should be labeled as "other".
    missing_clades = set(clades) - set(model_clades) - {"other"}
    if len(missing_clades) > 0:
        print(f"ERROR: The following required clades are missing from the model JSON: {missing_clades}", file=sys.stderr)
        sys.exit(1)

    modeled_clade_to_required_clade = {clade: clade for clade in clades}
    modeled_clade_to_required_clade["other"] = "other"
    for clade in model_clades:
        if clade not in modeled_clade_to_required_clade:
            modeled_clade_to_required_clade[clade] = "other"

    print(f"Mapping modeled clades to required clades: {modeled_clade_to_required_clade}")

    # Load map of full state/territory names to two-letter abbreviations.
    state_to_abbreviation_map = dict(
        pd.read_csv(
            args.state_to_abbreviation_map,
        ).values
    )

    # Extract the required number of samples from the posterior for estimated
    # current and future frequencies. The posterior JSON contains one set of
    # nested arrays per parameter (e.g., freq, freq_forecast, ga, etc.) in the
    # shape of (N_SAMPLES, N_DATES, N_VARIANTS, N_LOCATIONS) with "hierarchical"
    # included as one of the locations.
    with open(args.posterior, "r", encoding="utf-8") as fh:
        posterior = json.load(fh)

    # Select the latest N samples from the posterior.
    posterior_frequencies = posterior["freq"][-min_samples:]
    posterior_forecast_frequencies = posterior["freq_forecast"][-min_samples:]
    del posterior

    print(f"Posterior samples: {len(posterior_frequencies)}")

    records = []
    for sample_index in range(min_samples):
        for date in target_dates:
            # Target dates can be represented in the model JSON either as
            # nowcasts or forecasts. We need to check the membership of the date
            # in these two lists of dates.
            if date in model_dates:
                frequency_data = posterior_frequencies
                date_index = model_dates.index(date)
            elif date in model_forecast_dates:
                frequency_data = posterior_forecast_frequencies
                date_index = model_forecast_dates.index(date)
            else:
                continue

            for location_index, location in enumerate(model_locations):
                # Look up ISO-3166-1 alpha-2 codes for full state/territory names
                # from the model
                location_label = state_to_abbreviation_map[location]

                for clade, clade_label in modeled_clade_to_required_clade.items():
                    if clade == "other" and clade not in model_clades:
                        # Force-include entries with zeros for "other" group, if
                        # it is a required clade and not present in the model.
                        value = 0.0
                    else:
                        clade_index = model_clades.index(clade)
                        value = round(frequency_data[sample_index][date_index][clade_index][location_index], MAX_PRECISION)

                    records.append({
                        "nowcast_date": nowcast_date,
                        "target_date": date,
                        "location": location_label,
                        "clade": clade_label,
                        "output_type": "sample",
                        "output_type_id": f"{location_label}{sample_index + 1}",
                        "value": value,
                    })

    # Recalculate total frequencies per date, location, sample, and clade to
    # account for non-required clades that mapped to the "other" group.
    records = pd.DataFrame(records).groupby(
        [
            "nowcast_date",
            "target_date",
            "location",
            "clade",
            "output_type",
            "output_type_id",
        ],
        sort=False,
    ).aggregate(
        value=("value", "sum"),
    ).reset_index()

    # Check that all the data we expect are in the final data frame.
    # Clades are all required.
    assert set(clades) == set(records["clade"])

    # Target dates and locations are optional, so the observed lists in the
    # records should be subsets of the hub-specified lists.
    assert set(records["target_date"]) <= set(target_dates)
    assert set(records["location"]) <= set(locations)

    # All frequencies per location/sample and date should sum to 1.
    all_frequencies = records.groupby(["output_type_id", "target_date"])["value"].sum().values
    assert np.allclose(all_frequencies, np.ones(all_frequencies.shape))

    # Save estimates to a parquet file.
    records.to_parquet(args.output)
