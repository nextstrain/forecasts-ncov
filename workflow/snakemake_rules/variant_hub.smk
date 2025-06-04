from pathlib import Path

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
        clades="hub/included_clades.tsv",
    shell:
        r"""
        jq -r '.rounds[-1].model_tasks[0].task_ids.clade.required | map([., .]) | map(join("\t")) | .[]' {input.tasks:q} > {output.clades:q}
        """

def _get_model_json_for_model_abbr(wildcards):
    model_parameters = config["hub_models"][wildcards.model_abbr]
    model_parameters["date"] = wildcards.date

    return "results/{data_provenance}/{variant_classification}/{geo_resolution}/mlr/model-outputs/{date}_results.json".format(
        **model_parameters,
    )

def _get_posterior_json_for_model_abbr(wildcards):
    model_parameters = config["hub_models"][wildcards.model_abbr]

    return "results/{data_provenance}/{variant_classification}/{geo_resolution}/mlr/model-outputs/models/hierarchical.json".format(
        **model_parameters,
    )

rule prepare_hub_submission:
    input:
        tasks="hub/tasks.json",
        model=_get_model_json_for_model_abbr,
        state_to_abbreviation_map="config/state_to_abbreviation_map.csv",
    output:
        submission="hub/model-output/{hub_team_name}-{model_abbr}/{date}-{hub_team_name}-{model_abbr}.parquet",
    params:
        # TODO: The posterior should eventually be an explicit output of the
        # run-model script, so we can refer to it here as an explicit input
        # instead of a parameter. For now, we expect that this posterior file
        # exists when the main model JSON exists.
        posterior=_get_posterior_json_for_model_abbr,
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
    date = config.get("run_date", get_todays_date())

    return [
        "hub/model-output/{hub_team_name}-{model_abbr}/{date}-{hub_team_name}-{model_abbr}.parquet".format(
            hub_team_name=config["hub_team_name"],
            model_abbr=model_abbr,
            date=date,
        )
        for model_abbr in config["hub_models"]
    ]

rule prepare_all_hub_submissions:
    input:
        submissions=_get_all_hub_submissions,
    output:
        submissions="hub/submissions.txt",
    params:
        relative_submissions=lambda wildcards, input: [Path(submission).relative_to("hub").as_posix() for submission in input.submissions],
    shell:
        r"""
        for submission in {params.relative_submissions};
        do
            echo ${{submission}};
        done > {output.submissions}
        """
