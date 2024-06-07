"""
This part of the workflow summarizes SARS-CoV-2 case counts from public
exteranl data sources (e.g. Our World in Data) and uploads them to AWS S3 for
downstream use by the modeling workflow.
"""


rule fetch_global_case_counts:
    output:
        global_case_counts = "data/global_case_counts.tsv",
    shell:
        """
        ./bin/fetch-ncov-global-case-counts > {output.global_case_counts}
        """


rule upload_global_case_counts:
    input:
        global_case_counts = "data/global_case_counts.tsv",
    output:
        upload_flag = "results/upload_global_case_counts.done",
    params:
        s3_dst = config["s3_dst"],
        cloudfront_domain = config["cloudfront_domain"],
    shell:
        """
        ./vendored/upload-to-s3 \
            {input.global_case_counts} \
            {params.s3_dst}/cases/global.tsv.gz \
            {params.cloudfront_domain:q} 2>&1 | tee {output.upload_flag}
        """
