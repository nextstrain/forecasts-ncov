"""
This part of the workflow runs the model scripts.
"""

rule renewal_model:
    input:
        cases = "data/{data_provenance}/{geo_resolution}/prepared_cases.tsv",
        variants = "data/{data_provenance}/{geo_resolution}/prepared_variants.tsv"
    output:
        export = directory("results/{data_provenance}/{geo_resolution}/renewal")
    log:
        "logs/{data_provenance}/{geo_resolution}/renewal_model.txt"
    benchmark:
        "benchmarks/{data_provenance}/{geo_resolution}/renewal_model.txt"
    params:
        renewal_config = config.get("renewal_config")
    resources:
        mem_mb=4000
    shell:
        """
        python -u ./scripts/run-renewal-model.py \
            --config {params.renewal_config} \
            --case-path {input.cases} \
            --seq-path {input.variants} \
            --export-path {output.export} 2>&1 | tee {log}
        """


rule mlr_model:
    input:
        variants = "data/{data_provenance}/{geo_resolution}/prepared_variants.tsv"
    output:
        export = directory("results/{data_provenance}/{geo_resolution}/mlr")
    log:
        "logs/{data_provenance}/{geo_resolution}/mlr_model.txt"
    benchmark:
        "benchmarks/{data_provenance}/{geo_resolution}/mlr_model.txt"
    params:
        renewal_config = config.get("mlr_config")
    resources:
        mem_mb=4000
    shell:
        """
        python -u ./scripts/run-mlr-model.py \
            --config {params.renewal_config} \
            --seq-path {input.variants} \
            --export-path {output.export} 2>&1 | tee {log}
        """