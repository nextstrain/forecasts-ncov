import os

if not config:
    configfile: "config/config.yaml"

if not config.get("data_provenances"):
    print("ERROR: config must include 'data_provenances'.")
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

def _get_all_input(w):
    data_provenances = config["data_provenances"]
    geo_resolutions = config["geo_resolutions"]

    all_input = [
        *expand(
            "data/{data_provenance}/{geo_resolution}/prepared_cases.tsv",
            data_provenance=data_provenances,
            geo_resolution=geo_resolutions
        ),
        *expand(
            "data/{data_provenance}/{geo_resolution}/prepared_variants.tsv",
            data_provenance=data_provenances,
            geo_resolution=geo_resolutions
        )
    ]

    if config.get("send_slack_notifications"):
        all_input.extend(expand(
            "data/{data_provenance}/{geo_resolution}/notify/clade_without_variant.done",
            data_provenance=data_provenances,
            geo_resolution=geo_resolutions
        ))

    if config.get("renewal_config"):
        all_input.extend(expand(
            "results/{data_provenance}/{geo_resolution}/renewal_model",
            data_provenance=data_provenances,
            geo_resolution=geo_resolutions
        ))

    if config.get("mlr_config"):
        all_input.extend(expand(
            "results/{data_provenance}/{geo_resolution}/mlr_model",
            data_provenance=data_provenances,
            geo_resolution=geo_resolutions
        ))

    return all_input


rule all:
    input: _get_all_input


include: "workflow/snakemake_rules/prepare_data.smk"
include: "workflow/snakemake_rules/models.smk"

if config.get("send_slack_notifications"):
    include: "workflow/snakemake_rules/slack_notifications.smk"
