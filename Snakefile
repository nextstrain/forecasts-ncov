import os

KNOWN_MODELS = ["mlr", "renewal"]

if not config:
    configfile: "config/config.yaml"

if not config.get("data_provenances"):
    print("ERROR: config must include 'data_provenances'.")
    sys.exit(1)

if not config.get("variant_classifications"):
    print("ERROR: config must include 'variant_classifications'.")
    sys.exit(1)

if not config.get("geo_resolutions"):
    print("ERROR: config must include 'geo_resolutions'.")
    sys.exit(1)

if config.get("send_slack_notifications"):
    # Check that the required environment variables are set for Slack notifications
    required_envvar = ["SLACK_TOKEN", "SLACK_CHANNELS"]
    if any(envvar not in os.environ for envvar in required_envvar):
        print(f"ERROR: Must set the following environment variables to send Slack notifications: {required_envvar}")
        sys.exit(1)

wildcard_constraints:
    date = r"\d{4}-\d{2}-\d{2}"

def get_todays_date():
    from datetime import datetime
    date = datetime.today().strftime('%Y-%m-%d')
    return date

# Check which models to run based on which model configs have been provided
models_to_run = [
    model_name
    for model_name in KNOWN_MODELS
    if config.get(f"{model_name}_config")
]

def _get_all_input(w):
    data_provenances = config["data_provenances"] if isinstance(config["data_provenances"], list) else [config["data_provenances"]]
    variant_classifications = config["variant_classifications"] if isinstance(config["variant_classifications"], list) else [config["variant_classifications"]]
    geo_resolutions = config["geo_resolutions"] if isinstance(config["geo_resolutions"], list) else [config["geo_resolutions"]]

    all_input = [
        *expand(
            "data/{data_provenance}/{variant_classification}/{geo_resolution}/prepared_cases.tsv",
            data_provenance=data_provenances,
            variant_classification=variant_classifications,
            geo_resolution=geo_resolutions
        ),
        *expand(
            "data/{data_provenance}/{variant_classification}/{geo_resolution}/prepared_seq_counts.tsv",
            data_provenance=data_provenances,
            variant_classification=variant_classifications,
            geo_resolution=geo_resolutions
        )
    ]

    if models_to_run:
        run_date = config.get("run_date", get_todays_date())
        all_input.extend(expand(
            "results/{data_provenance}/{variant_classification}/{geo_resolution}/{model}/{date}_results.json",
            data_provenance=data_provenances,
            variant_classification=variant_classifications,
            geo_resolution=geo_resolutions,
            model=models_to_run,
            date=run_date
        ))
        if config.get("s3_dst"):
            all_input.extend(expand(
                [
                    "results/{data_provenance}/{variant_classification}/{geo_resolution}/{model}/{date}_results_s3_upload.done",
                    "results/{data_provenance}/{variant_classification}/{geo_resolution}/{model}/{date}_latest_results_s3_upload.done"
                ],
                data_provenance=data_provenances,
                variant_classification=variant_classifications,
                geo_resolution=geo_resolutions,
                model=models_to_run,
                date=run_date
            ))

    return all_input


rule all:
    input: _get_all_input


include: "workflow/snakemake_rules/prepare_data.smk"
include: "workflow/snakemake_rules/models.smk"

if config.get("send_slack_notifications"):
    include: "workflow/snakemake_rules/slack_notifications.smk"

if config.get("s3_dst"):
    include: "workflow/snakemake_rules/upload.smk"

if config.get("tasks_url"):
    include: "workflow/snakemake_rules/variant_hub.smk"
