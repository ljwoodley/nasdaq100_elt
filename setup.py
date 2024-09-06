from setuptools import find_packages, setup

setup(
    name="nasdaq100_elt",
    packages=find_packages(exclude=["nasdaq100_elt_tests"]),
    install_requires=[
        "dagster==1.8.4",
        "dagster-dbt==0.24.4",
        "dagster-duckdb==0.24.4",
        "dbt-duckdb==1.8.3",
        "pandas==2.2.2",
        "yfinance==0.2.43",
        "pydantic==2.8.2"
    ],
    extras_require={
        "dev": [
            "dagster-webserver==1.8.4",
            "pytest==8.3.2"
        ],
        "dashboard": [
            "itables==2.1.4",
            "nbformat==5.10.4",
            "nbclient==0.10.0",
            "matplotlib==3.9.2",
            "plotly==5.24.0",
            "ipykernel==6.29.5"
        ]
    }
)
