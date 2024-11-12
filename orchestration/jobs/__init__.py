from dagster import AssetSelection, define_asset_job, job, op
import os
import subprocess


@op
def render_dashboard():
    file_path = os.path.join("dashboard", "dashboard.qmd")
    subprocess.run(["uv", "run", "quarto", "render", file_path])


@job
def render_dashboard_job():
    render_dashboard()


ingest_and_transform_job = define_asset_job(
    name="ingest_and_transform_job",
    selection=AssetSelection.all()
)
