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
