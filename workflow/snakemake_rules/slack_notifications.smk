"""
This part of the workflow handles Slack notifications.
"""

onstart:
    shell("./bin/notify-on-job-start")


onerror:
    shell("./bin/notify-on-job-fail")
