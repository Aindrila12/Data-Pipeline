# app.py

import importlib
import yaml
import argparse
import logging
from core.interfaces import Fetcher, Writer
from core.data_wrapper import DataWrapper
from utility.logger import setup_logger
from inspect import signature

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

    for task in config.get("pipeline", []):
        if not task.get("enabled", True):
            logger.info(f"Skipping disabled pipeline: {task.get('name')}")
            continue

        task_name = task.get("name", "Unnamed Pipeline")
        logger.info(f"Starting pipeline: {task_name}")

        # --- Fetcher setup ---
        fetcher_cfg = task.get("fetcher", {})
        fetcher_class = load_class(fetcher_cfg["class"])
        fetcher_params = fetcher_cfg.get("params", {})
        fetcher = fetcher_class(**fetcher_params)

        if not isinstance(fetcher, Fetcher):
            logger.error(f"{fetcher.__class__.__name__} does not implement Fetcher Interface")
            continue

        if hasattr(fetcher, "initialize"):
            fetcher.initialize()

        fetch_operation = fetcher_cfg.get("operation", "fetch_data")
        fetch_operation_params = fetcher_cfg.get("operation_params", {})  # ✅ NEW
        fetch_ops = fetcher.get_operations()
        fetch_method = fetch_ops.get(fetch_operation, getattr(fetcher, fetch_operation, None))

        if not callable(fetch_method):
            logger.error(f"Fetcher operation '{fetch_operation}' not found.")
            continue

        logger.info(f"Fetching data using operation: {fetch_operation} with params: {fetch_operation_params}")
        data: DataWrapper = fetch_method(**fetch_operation_params)  # ✅ UPDATED
        print("********data********", data)

        # --- Writers ---
        for writer_cfg in task.get("writers", []):
            writer_class = load_class(writer_cfg["class"])
            writer_params = writer_cfg.get("params", {})
            writer = writer_class(**writer_params)

            if not isinstance(writer, Writer):
                logger.error(f"{writer.__class__.__name__} does not implement Writer Interface")
                continue

            if hasattr(writer, "initialize"):
                writer.initialize()

            write_operation = writer_cfg.get("operation", "write_data")
            # Load data and operation_params
            data_list = writer_cfg.get("data", [])
            write_operation_params = writer_cfg.get("operation_params", {})  # ✅ NEW
            write_ops = writer.get_operations()
            write_method = write_ops.get(write_operation, getattr(writer, write_operation, None))

            if not callable(write_method):
                logger.error(f"Writer operation '{write_operation}' not found.")
                continue

            logger.info(f"Writing data using operation: {write_operation} with params: {write_operation_params}")
            # if write_operation_params:
            #     write_method(data, **write_operation_params)  # ✅ UPDATED
            # else:
            #     write_method(data)
            # write_method(writer, data)
            method_sig = signature(write_method)
            param_count = len(method_sig.parameters)
            # print("param count >>>>>>>>>", param_count)

            if param_count == 0:
                write_method()
            elif param_count == 1:
                write_method(data)
            else:
                write_method(data, **write_operation_params)

        logger.info(f"Pipeline '{task_name}' completed.")


def list_enabled_operations(config_path):
    print(f"\nReading config from {config_path}...")
    with open(config_path, "r") as file:
        config = yaml.safe_load(file)

    printed = False
    for task in config.get("pipeline", []):
        if not task.get("enabled", True):
            continue

        print(f"\n▶ Enabled Pipeline: {task.get('name')}")

        # Fetcher
        fetcher_cfg = task.get("fetcher", {})
        if fetcher_cfg:
            fetcher_class = load_class(fetcher_cfg["class"])
            fetcher_params = fetcher_cfg.get("params", {})
            fetcher = fetcher_class(**fetcher_params)
            print(f"\n  🔹 Fetcher: {fetcher_class.__name__}")
            ops = fetcher.get_operations()
            for op_name, func in ops.items():
                print(f"    - {op_name}: {func.__doc__ or 'No doc'}")
            printed = True

        # Writers
        for writer_cfg in task.get("writers", []):
            writer_class = load_class(writer_cfg["class"])
            writer_params = writer_cfg.get("params", {})
            writer = writer_class(**writer_params)
            print(f"\n  🔸 Writer: {writer_class.__name__}")
            ops = writer.get_operations()
            for op_name, func in ops.items():
                print(f"    - {op_name}: {func.__doc__ or 'No doc'}")
            printed = True

    if not printed:
        print("⚠ No enabled fetchers or writers found.")





def main():
    setup_logger()

    parser = argparse.ArgumentParser(description="Run the data pipeline")
    parser.add_argument(
        "--config", "-c", default="config/config.yaml", help="Path to the YAML config file"
    )
    parser.add_argument(
        "--list-ops", action="store_true", help="List available operations of enabled fetchers/writers"
    )
    args = parser.parse_args()
    # print(">>>>>>>>>>>>", args)

    if args.list_ops:
        list_enabled_operations(args.config)
    else:
        process_pipeline(args.config)

if __name__ == "__main__":
    main()
