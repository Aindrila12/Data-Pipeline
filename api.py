from app import process_pipeline
import yaml

def run_pipeline_from_file(config_path: str):
    process_pipeline(config_path)

def run_pipeline_from_dict(config_dict: dict):
    process_pipeline(config_dict)
