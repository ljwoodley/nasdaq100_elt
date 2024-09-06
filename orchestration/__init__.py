from dagster import Definitions, load_assets_from_package_module
from dagster_dbt import DbtCliResource
from dagster_duckdb import DuckDBResource

from . import assets
from .project import dbt_project

defs = Definitions(
    assets=load_assets_from_package_module(assets),
    resources={
        "dbt": DbtCliResource(project_dir=dbt_project),
        "database": DuckDBResource(
            database="data/database.duckdb"
        )
    }
)
