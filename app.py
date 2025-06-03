# app.py

import importlib
import yaml
import argparse
import logging
from core.interfaces import Fetcher, Writer
from core.data_wrapper import DataWrapper
from utility.logger import setup_logger

def load_class(full_class_string):
    """Dynamically load a class from a string"""
    module_path, class_name = full_class_string.rsplit(".", 1)
    module = importlib.import_module(module_path)
    return getattr(module, class_name)

def process_pipeline(config_path: str):
    logger = logging.getLogger("pipeline")
    logger.info(f"Reading config: {config_path}")

    with open(config_path, "r") as file:
        config = yaml.safe_load(file)

    for fetcher_cfg in config.get("fetchers", []):
        fetcher_class = load_class(fetcher_cfg["class"])
        fetcher_params = fetcher_cfg.get("params", {})
        fetcher = fetcher_class(**fetcher_params)

        if not isinstance(fetcher, Fetcher):
            raise TypeError(f"{fetcher.__class__.__name__} does not implement Fetcher Interface")

        logger.info(f"Fetching data using {fetcher.__class__.__name__}")
        data: DataWrapper = fetcher.fetch_data()

        for writer_cfg in config.get("writers", []):
            writer_class = load_class(writer_cfg["class"])
            writer_params = writer_cfg.get("params", {})
            writer = writer_class(**writer_params)

            if not isinstance(writer, Writer):
                raise TypeError(f"{writer.__class__.__name__} does not implement Writer Interface")

            logger.info(f"Writing data using {writer.__class__.__name__}")
            writer.write_data(data)

def main():
    setup_logger()

    parser = argparse.ArgumentParser(description="Run the data pipeline")
    parser.add_argument(
        "--config", "-c", default="config.yaml", help="Path to the YAML config file"
    )
    args = parser.parse_args()

    process_pipeline(args.config)

if __name__ == "__main__":
    main()
