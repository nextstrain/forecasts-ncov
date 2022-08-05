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

rule download_open_data:
    message: "Downloading case counts and Nextstrain clade counts from data.nextstrain.org"
    wildcard_constraints:
        geo_resolution = "global|usa"
    output:
        cases = "data/open/{geo_resolution}/cases.tsv.gz",
        nextstrain_clades = "data/open/{geo_resolution}/nextstrain_clades.tsv.gz"
    params:
        cases_url = "https://data.nextstrain.org/files/workflows/forecasts-ncov/{geo_resolution}/cases.tsv.gz",
        nextstrain_clades_url = "https://data.nextstrain.org/files/workflows/forecasts-ncov/{geo_resolution}/nextstrain_clades.tsv.gz"
    shell:
        """
        curl -fsSL --compressed {params.cases_url:q} --output {output.cases}
        curl -fsSL --compressed {params.nextstrain_clades_url:q} --output {output.nextstrain_clades}
        """

rule download_gisaid_data:
    message: "Downloading case counts and Nextstrain clade counts from s3://nextstrain-data-private"
    wildcard_constraints:
        geo_resolution = "global|usa"
    output:
        cases = "data/gisaid/{geo_resolution}/cases.tsv.gz",
        nextstrain_clades = "data/gisaid/{geo_resolution}/nextstrain_clades.tsv.gz"
    params:
        cases_url = "s3://nextstrain-data-private/files/workflows/forecasts-ncov/{geo_resolution}/cases.tsv.gz",
        nextstrain_clades_url = "s3://nextstrain-data-private/files/workflows/forecasts-ncov/{geo_resolution}/nextstrain_clades.tsv.gz"
    shell:
        """
        aws s3 cp --no-progress {params.cases_url:q} {output.cases}
        aws s3 cp --no-progress {params.nextstrain_clades_url:q} {output.nextstrain_clades}
        """

def _get_prepare_data_option(wildcards, option_name):
    """
    Return the option for prepare data from the config based on the
    wildcards.data_provenance and the wildcards.geo_resolution values.

    If the *option* exists as a key within config['prepare_data'][wildcard.data_provenance][wildcard.geo_resolution]
    then return as "--{option-name} {option_value}". Or else return an empty string.
    """
    option_value = config.get('prepare_data', {}) \
                         .get(wildcards.data_provenance, {}) \
                         .get(wildcards.geo_resolution, {}) \
                         .get(option_name)

    if option_value is not None:
        # Change underscores of YAML keys to dashes for proper CLI option names
        option_name = option_name.replace('_', '-')
        return f'--{option_name} {option_value}'

    return ''


rule prepare_data:
    message: "Preparing counts data for analysis"
    input:
        cases = "data/{data_provenance}/{geo_resolution}/cases.tsv.gz",
        nextstrain_clades = "data/{data_provenance}/{geo_resolution}/nextstrain_clades.tsv.gz"
    output:
        clade_without_variant = "data/{data_provenance}/{geo_resolution}/clade_without_variant.txt",
        cases = "data/{data_provenance}/{geo_resolution}/prepared_cases.tsv",
        variants = "data/{data_provenance}/{geo_resolution}/prepared_variants.tsv"
    log:
        "logs/{data_provenance}/{geo_resolution}/prepare_data.txt"
    params:
        max_date = lambda wildcards: _get_prepare_data_option(wildcards, 'max_date'),
        included_days = lambda wildcards: _get_prepare_data_option(wildcards, 'included_days'),
        location_min_seq = lambda wildcards: _get_prepare_data_option(wildcards, 'location_min_seq'),
        location_min_seq_days = lambda wildcards: _get_prepare_data_option(wildcards, 'location_min_seq_days'),
        excluded_locations = lambda wildcards: _get_prepare_data_option(wildcards, 'excluded_locations'),
        prune_seq_days = lambda wildcards: _get_prepare_data_option(wildcards, 'prune_seq_days'),
        clade_min_seq = lambda wildcards: _get_prepare_data_option(wildcards, 'clade_min_seq'),
        clade_min_seq_days = lambda wildcards: _get_prepare_data_option(wildcards, 'clade_min_seq_days'),
        clade_to_variant = lambda wildcards: _get_prepare_data_option(wildcards, 'clade_to_variant'),
        force_include_clades = lambda wildcards: _get_prepare_data_option(wildcards, 'force_include_clades'),
    shell:
        """
        python ./scripts/prepare-data.py \
            --clades {input.nextstrain_clades} \
            --cases {input.cases} \
            {params.max_date} \
            {params.included_days} \
            {params.location_min_seq} \
            {params.location_min_seq_days} \
            {params.excluded_locations} \
            {params.prune_seq_days} \
            {params.clade_min_seq} \
            {params.clade_min_seq_days} \
            {params.clade_to_variant} \
            {params.force_include_clades} \
            --output-clade-without-variant {output.clade_without_variant} \
            --output-variants {output.variants} \
            --output-cases {output.cases} 2>&1 | tee {log}
        """
