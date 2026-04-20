"""
This part of the workflow handles Slack notifications.
"""

onstart:
    shell("./ingest/vendored/scripts/notify-on-job-start 'Run model' 'nextstrain/forecasts-ncov' '.' ")


onerror:
    shell("./ingest/vendored/scripts/notify-on-job-fail 'Run model' 'nextstrain/forecasts-ncov'")
