from setuptools import setup, find_packages

setup(
    name="data-pipeline",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "google-api-python-client",
        "google-auth",
        "google-auth-oauthlib",
        "dropbox",
        "pyyaml",
        "loguru",
        "gspread",
        "oauthlib",
        "pyairtable",
        "slack-sdk",
        "simple-salesforce"
    ],
    entry_points={
        'console_scripts': [
            'run-pipeline=DATA_PIPELINE.api:run_pipeline_from_file'
        ]
    },
    include_package_data=True,
    zip_safe=False
)
