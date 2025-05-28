envvars:
    "GIT_AUTHOR_EMAIL",
    "GIT_AUTHOR_NAME",
    "GITHUB_TOKEN",

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

rule push_all_hub_submissions:
    input:
        submissions=_get_all_hub_submissions,
    output:
        submission_flag=touch("hub/submission_pushed.txt"),
    params:
        hub_github_fork_url=config["hub_github_fork_url"],
        hub_github_directory="hub/variant-nowcast-hub",
        hub_team_name=config["hub_team_name"],
        date=config.get("run_date", get_todays_date()),
    shell:
        r"""
        git config --global user.email "${{GIT_AUTHOR_EMAIL}}";
        git config --global user.name "${{GIT_AUTHOR_NAME}}";

        rm -rf {params.hub_github_directory};
        git clone --no-tags --depth=1 https://${{GITHUB_TOKEN}}@{params.hub_github_fork_url:q} {params.hub_github_directory};

        cp -R hub/model-output/* {params.hub_github_directory}/model-output/;
        cd {params.hub_github_directory};

        git checkout -b {params.hub_team_name}-{params.date};
        git add -A model-output/;
        git commit -m "Add {params.hub_team_name} models for {params.date}";
        git push origin {params.hub_team_name}-{params.date};
        """
