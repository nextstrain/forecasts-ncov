"""
This part of the workflow handles uploading files to specific locations.

Uses predefined wildcards `data_provenance`, `variant_classification`, `geo_resolution`, `model
and `date` to determine inputs and upload destination.

Produces output files as `results/{data_provenance}/{variant_classification}/{geo_resolution}/{model}/{date}*upload.done`.

Currently only supports uploads to AWS S3, but additional upload rules can
be easily added as long as they follow the output pattern described above.
"""
import os
import yaml
from pathlib import Path

slack_envvars_defined = "SLACK_CHANNELS" in os.environ and "SLACK_TOKEN" in os.environ
send_notifications = (
    config.get("send_slack_notifications", False) and slack_envvars_defined
)

def _get_s3_url(w, input_file):
    s3_dst = config["s3_dst"].rstrip("/")
    s3_path = Path(input_file).relative_to("results")

    # The last part of the path should always be the model name
    while s3_path.stem != w.model:
        s3_path = s3_path.parent

    return f"{s3_dst}/{s3_path}/"

rule upload_model_results_to_s3:
    input:
        model_results = "results/{data_provenance}/{variant_classification}/{geo_resolution}/{model}/{date}_results.json"
    output:
        touch("results/{data_provenance}/{variant_classification}/{geo_resolution}/{model}/{date}_results_s3_upload.done")
    params:
        quiet="" if send_notifications else "--quiet",
        s3_url=lambda w, input: _get_s3_url(w, input.model_results),
    shell:
        """
        ./bin/nextstrain-remote-upload-with-slack-notification \
            {params.quiet} \
            {params.s3_url} \
            {input.model_results}
        """

rule copy_dated_model_results_to_latest:
    input:
        dated_model_results = "results/{data_provenance}/{variant_classification}/{geo_resolution}/{model}/{date}_results.json"
    output:
        latest_model_results = "results/{data_provenance}/{variant_classification}/{geo_resolution}/{model}/{date}/latest_results.json"
    shell:
        """
        cp {input.dated_model_results} {output.latest_model_results}
        """

rule upload_model_results_to_s3_as_latest:
    input:
        model_results = "results/{data_provenance}/{variant_classification}/{geo_resolution}/{model}/{date}/latest_results.json"
    output:
        touch("results/{data_provenance}/{variant_classification}/{geo_resolution}/{model}/{date}_latest_results_s3_upload.done")
    params:
        quiet="" if send_notifications else "--quiet",
        s3_url=lambda w, input: _get_s3_url(w, input.model_results),
    shell:
        """
        ./bin/nextstrain-remote-upload-with-slack-notification \
            {params.quiet} \
            {params.s3_url} \
            {input.model_results}
        """
