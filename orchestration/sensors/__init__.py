from dagster import (
    run_status_sensor,
    DagsterRunStatus,
    RunRequest,
    DefaultSensorStatus
)

from ..jobs import render_dashboard_job, ingest_and_transform_job


@run_status_sensor(
    run_status=DagsterRunStatus.SUCCESS,
    default_status=DefaultSensorStatus.RUNNING,
    monitored_jobs=[ingest_and_transform_job],
    request_job=render_dashboard_job,
)
def ingest_and_transform_sensor(context):
    return RunRequest()
