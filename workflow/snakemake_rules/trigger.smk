"""
This part of the workflow triggers downstream GitHub Action workflows.

Requires `models_to_run` variable to be defined upstream.
"""

def _get_trigger_static_model_viz_input(wildcards):
    return [
        f"results/gisaid/nextstrain_clades/global/{model}/{wildcards.date}_latest_results_s3_upload.done"
        for model in models_to_run
    ]


rule trigger_static_model_viz:
    input: _get_trigger_static_model_viz_input
    output:
        touch("results/gisaid/nextstrain_clades/global/{date}_trigger_static_model_viz.done")
    shell:
        """
        ./bin/trigger forecasts-ncov static-model-viz
        """

