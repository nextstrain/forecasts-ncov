"""
This part of the workflow handles uploading files to specific locations.

Uses predefined wildcards `data_provenance`,`geo_resolution`, `model`, and `date`
to determine inputs and upload destination.

Produces output files as `results/{data_provenance}/{geo_resolution}/{model}/{date}*upload.done`.

Currently only supports uploads to AWS S3, but additional upload rules can
be easily added as long as they follow the output pattern described above.
"""
import os
import yaml

slack_envvars_defined = "SLACK_CHANNELS" in os.environ and "SLACK_TOKEN" in os.environ
send_notifications = (
    config.get("send_slack_notifications", False) and slack_envvars_defined
)

rule upload_case_counts_to_s3:
    input:
        case_counts = "data/{geo_resolution}_case_counts.tsv"
    output:
        upload_flag = "data/{data_provenance}/{geo_resolution}_case_counts_upload.done"
    params:
        quiet="" if send_notifications else "--quiet",
        s3_dst=lambda wildcards: config["upload"].get(wildcards.data_provenance, {}).get("s3_dst", ""),
        cloudfront_domain=lambda wildcards: config["upload"].get(wildcards.data_provenance, {}).get("cloudfront_domain", "")
    shell:
        """
        ./ingest/bin/upload-to-s3 \
            {params.quiet} \
            {input.model_results:q} \
            {params.s3_dst:q}/{wildcards.geo_resolution:q}/cases.tsv.gz \
            {params.cloudfront_domain} 2>&1 | tee {output.upload_flag}
        """

rule upload_clade_counts_to_s3:
    input:
        clade_counts = "data/{data_provenance}/{geo_resolution}/nextstrain_clade_counts.tsv"
    output:
        upload_flag = "data/{data_provenance}/{geo_resolution}/nextstrain_clade_counts_upload.done"
    params:
        quiet="" if send_notifications else "--quiet",
        s3_dst=lambda wildcards: config["upload"].get(wildcards.data_provenance, {}).get("s3_dst", ""),
        cloudfront_domain=lambda wildcards: config["upload"].get(wildcards.data_provenance, {}).get("cloudfront_domain", "")
    shell:
        """
        ./ingest/bin/upload-to-s3 \
            {params.quiet} \
            {input.model_results:q} \
            {params.s3_dst:q}/{wildcards.geo_resolution:q}/nextstrain_clades.tsv.gz \
            {params.cloudfront_domain} 2>&1 | tee {output.upload_flag}
        """

rule upload_model_results_to_s3:
    input:
        model_results = "results/{data_provenance}/{geo_resolution}/{model}/{date}_results.json"
    output:
        upload_flag = "results/{data_provenance}/{geo_resolution}/{model}/{date}_results_s3_upload.done"
    params:
        quiet="" if send_notifications else "--quiet",
        s3_dst=lambda wildcards: config["upload"].get(wildcards.data_provenance, {}).get("s3_dst", ""),
        cloudfront_domain=lambda wildcards: config["upload"].get(wildcards.data_provenance, {}).get("cloudfront_domain", "")
    shell:
        """
        ./ingest/bin/upload-to-s3 \
            {params.quiet} \
            {input.model_results:q} \
            {params.s3_dst:q}/{wildcards.geo_resolution:q}/{wildcards.model:q}/{wildcards.date}_results.json.zst \
            {params.cloudfront_domain} 2>&1 | tee {output.upload_flag}
        """
