"""
This part of the workflow downloads and prepares the data necessary to run models
"""

rule fetch_global_case_counts:
    message: "Fetching global case counts"
    output:
        global_case_counts = "data/global_case_counts.tsv"
    shell:
        """
        ./bin/fetch-ncov-global-case-counts > {output.global_case_counts}
        """

rule fetch_us_case_counts:
    message: "Fetching US case counts"
    output:
        us_case_counts = "data/usa_case_counts.tsv"
    shell:
        """
        ./bin/fetch-ncov-us-case-counts > {output.us_case_counts}
        """

rule fetch_metadata:
    message: "Fetching clean metadata produced by ncov-ingest"
    output:
        metadata = temp("data/{data_provenance}/metadata.tsv")
    params:
        s3_src = lambda w: config["data_provenances"][w.data_provenance]
    shell:
        """
        ./bin/download-from-s3 {params.s3_src} {output.metadata}
        """


rule subset_metadata:
    message: "Subsetting metadata to only required columns"
    input:
        metadata = "data/{data_provenance}/metadata.tsv"
    output:
        subset_metadata = "data/{data_provenance}/subset_metadata.tsv"
    params:
        subset_cols = "strain,date,country,division,QC_overall_status,Nextstrain_clade"
    shell:
        """
        tsv-select -H \
            -f {params.subset_cols} \
            {input.metadata} > {output.subset_metadata}
        """

def _get_clade_filter_columns(wildcards):
    filter_columns = "QC_overall_status"

    if wildcards.geo_resolution != "global":
        filter_columns += " country"

    return filter_columns


def _get_clade_filter_query(wildcards):
    filter_query = "QC_overall_status != 'bad'"

    if wildcards.geo_resolution == "usa":
        filter_query += " & country == 'USA'"

    return filter_query


rule summarize_clade_counts:
    message: "Summarizing clade counts"
    input:
        subset_metadata = "data/{data_provenance}/subset_metadata.tsv"
    output:
        clade_counts = "data/{data_provenance}/{geo_resolution}/nextstrain_clade_counts.tsv"
    params:
        filter_cols = _get_clade_filter_columns,
        filter_query = _get_clade_filter_query
    shell:
        """
        ./bin/summarize-clade-sequence-counts \
            --metadata {input.subset_metadata} \
            --clade-column Nexstrain_clade \
            --filter-columns {params.filter_cols} \
            --filter-query "{params.filter_query}" \
            --output {output.clade_counts}
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
        cases = "data/{geo_resolution}_case_counts.tsv",
        nextstrain_clades = "data/{data_provenance}/{geo_resolution}/nextstrain_clade_counts.tsv"
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
