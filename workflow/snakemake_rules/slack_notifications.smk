"""
This part of the workflow handles Slack notifications.
"""

rule notify_on_new_usa_locations:
    input:
        usa_case_counts = "data/usa_case_counts.tsv"
    output:
        touch("data/notify_on_new_usa_locations.done")
    params:
        usa_locations = "source-data/us-states.tsv"
    shell:
        """
        ./bin/notify-on-new-location {input.usa_case_counts} {params.usa_locations}
        """

rule notify_on_clade_without_variant:
    input:
        clade_without_variant = "data/{data_provenance}/{geo_resolution}/clade_without_variant.txt"
    output:
        touch("data/{data_provenance}/{geo_resolution}/notify/clade_without_variant.done")
    shell:
        """
        ./bin/notify-on-clade-without-variant {input.clade_without_variant}
        """
