rule download_tasks:
    output:
        tasks="hub/tasks.json",
    params:
        tasks_url=config["tasks_url"],
    shell:
        r"""
        curl -L -o {output.tasks:q} {params.tasks_url:q}
        """

rule parse_required_clades:
    """Create a list of required clades in format of 'clade=clade' required by the prepare data script."""
    input:
        tasks="hub/tasks.json",
    output:
        clades="hub/included_clades.txt",
    shell:
        r"""
        jq -r '.rounds[-1].model_tasks[0].task_ids.clade.required | map([., .]) | map(join("=")) | .[]' {input.tasks:q} > {output.clades:q}
        """

rule prepare_hub_submission:
    input:
        tasks="hub/tasks.json",
        model="results/{data_provenance}/{variant_classification}/{geo_resolution}/mlr/model-outputs/{date}_results.json",
        state_to_abbreviation_map="config/state_to_abbreviation_map.csv",
    output:
        submission="hub/model-output/{date}/{hub_team_name}/{data_provenance}/{variant_classification}/{geo_resolution}/mlr.parquet",
    params:
        # TODO: The posterior should eventually be an explicit output of the
        # run-model script, so we can refer to it here as an explicit input
        # instead of a parameter. For now, we expect that this posterior file
        # exists when the main model JSON exists.
        posterior="results/{data_provenance}/{variant_classification}/{geo_resolution}/mlr/model-outputs/models/hierarchical.json",
    shell:
        r"""
        python scripts/prepare_hub_submission.py \
            --hub-tasks {input.tasks:q} \
            --model {input.model:q} \
            --posterior {params.posterior:q} \
            --state-to-abbreviation-map {input.state_to_abbreviation_map:q} \
            --output {output.submission:q}
        """

def _get_all_hub_submissions(wildcards):
    base_hub_config = {
        "hub_team_name": config["hub_team_name"],
        "date": config.get("run_date", get_todays_date()),
    }

    return [
        "hub/model-output/{date}/{hub_team_name}/{data_provenance}/{variant_classification}/{geo_resolution}/mlr.parquet".format(
            **(hub_model | base_hub_config)
        )
        for hub_model in config["hub_models"]
    ]

rule prepare_all_hub_submissions:
    input:
        submissions=_get_all_hub_submissions,
