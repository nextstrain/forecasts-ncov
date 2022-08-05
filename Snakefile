if not config:
    configfile: "config/config.yaml"

if not config.get("data_provenances"):
    print("ERROR: config must include 'data_provenances'.")
    sys.exit(1)

if not config.get("geo_resolutions"):
    print("ERROR: config must include 'geo_resolutions'.")
    sys.exit(1)

rule all:
    input:
        prepared_cases = expand(
            "data/{data_provenance}/{geo_resolution}/prepared_cases.tsv",
            data_provenance=config["data_provenances"],
            geo_resolution=config["geo_resolutions"]
        ),
        prepared_variants = expand(
            "data/{data_provenance}/{geo_resolution}/prepared_variants.tsv",
            data_provenance=config["data_provenances"],
            geo_resolution=config["geo_resolutions"]
        )

include: "workflow/snakemake_rules/prepare_data.smk"
