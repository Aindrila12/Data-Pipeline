from app import process_pipeline
import yaml

def run_pipeline_from_file(config_path: str):
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    process_pipeline(config)

def run_pipeline_from_dict(config_dict: dict):
    process_pipeline(config_dict)
