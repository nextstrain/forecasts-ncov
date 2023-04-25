"""
This part of the workflow runs the model scripts.
"""

def _get_models_option(wildcards, option_name):
    """
    Return the option for model from the config based on the
    wildcards.data_provenance, wildcards.variant_classification and the wildcards.geo_resolution values.

    If the *option* exists as a key within config['models'][wildcard.data_provenance][wildcard.variant_classification][wildcard.geo_resolution]
    then return as "--{option-name} {option_value}". Or else return an empty string.
    """
    option_value = config.get('models', {}) \
                         .get(wildcards.data_provenance, {}) \
                         .get(wildcards.variant_classification, {}) \
                         .get(wildcards.geo_resolution, {}) \
                         .get(option_name)

    if option_value is not None:
        # Change underscores of YAML keys to dashes for proper CLI option names
        option_name = option_name.replace('_', '-')
        return f'--{option_name} {option_value}'

    return ''

rule renewal_model:
    input:
        cases = "data/{data_provenance}/{variant_classification}/{geo_resolution}/prepared_cases.tsv",
        sequence_counts = "data/{data_provenance}/{variant_classification}/{geo_resolution}/prepared_seq_counts.tsv"
    output:
        # Note this output is not used in the shell command because it is one of the many
        # files generated and output to the export path.
        # We are listing this specific file as the output file because it is the final
        # final output of the model script.
        results = "results/{data_provenance}/{variant_classification}/{geo_resolution}/renewal/{date}_results.json"
    log:
        "logs/{data_provenance}/{variant_classification}/{geo_resolution}/renewal/{date}.txt"
    benchmark:
        "benchmarks/{data_provenance}/{variant_classification}/{geo_resolution}/renewal/{date}.txt"
    params:
        renewal_config = config.get("renewal_config"),
        export_path = lambda w: f"results/{w.data_provenance}/{w.variant_classification}/{w.geo_resolution}/renewal"
    resources:
        mem_mb=4000
    shell:
        """
        python -u ./scripts/run-renewal-model.py \
            --config {params.renewal_config} \
            --case-path {input.cases} \
            --seq-path {input.sequence_counts} \
            --export-path {params.export_path} \
            --data-name {wildcards.date} 2>&1 | tee {log}
        """


rule mlr_model:
    input:
        sequence_counts = "data/{data_provenance}/{variant_classification}/{geo_resolution}/prepared_seq_counts.tsv"
    output:
        # Note this output is not used in the shell command because it is one of the many
        # files generated and output to the export path.
        # We are listing this specific file as the output file because it is the final
        # final output of the model script.
        results = "results/{data_provenance}/{variant_classification}/{geo_resolution}/mlr/{date}_results.json"
    log:
        "logs/{data_provenance}/{variant_classification}/{geo_resolution}/mlr/{date}.txt"
    benchmark:
        "benchmarks/{data_provenance}/{variant_classification}/{geo_resolution}/mlr/{date}.txt"
    params:
        renewal_config = config.get("mlr_config"),
        export_path = lambda w: f"results/{w.data_provenance}/{w.variant_classification}/{w.geo_resolution}/mlr",
        pivot = lambda wildcards: _get_models_option(wildcards, 'pivot')
    resources:
        mem_mb=4000
    shell:
        """
        python -u ./scripts/run-mlr-model.py \
            --config {params.renewal_config} \
            --seq-path {input.sequence_counts} \
            --export-path {params.export_path} \
            {params.pivot} \
            --data-name {wildcards.date} 2>&1 | tee {log}
        """
