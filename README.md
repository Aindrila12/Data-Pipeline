# Data Pipeline Framework

A modular, plugin-based data pipeline framework for fetching data from various sources (e.g., Google Docs, Google Sheets) and writing it to multiple destinations.  
The framework is fully configurable via YAML and supports custom fetchers and writers for seamless integration with other services.

---

## Overview

This framework allows you to:
- Fetch data from different services using **fetchers**.
- Process and write data using **writers**.
- Configure pipelines without modifying code.
- Plug in new integrations with minimal effort.

---

## Project Structure

```
DATA_PIPELINE/
│
├── app.py                   # Entry point: orchestrates the pipeline
├── api.py                   # Provides a callable interface for external apps
├── setup.py                 # Packaging and CLI entry points
│
├── config/                  # Configuration files
│   ├── config.yaml          # Pipeline definitions
│   └── auth_config.yaml     # Credentials and scopes
│
├── core/
│   ├── interfaces.py        # Abstract classes: Fetcher and Writer
│   ├── data_wrapper.py      # Standard wrapper for data and metadata
│
├── fetchers/                # Fetcher implementations
│   └── doc_fetcher.py
│   └── sheets_fetcher.py
│
├── writers/                 # Writer implementations
│   └── doc_writer.py
│   └── sheet_writer.py
│
└── utility/                 # Utility modules
    ├── auth.py              # Credential management
    └── logger.py            # Logging setup
```

---

## How It Works

1. **Configuration-Driven Execution**  
   Each pipeline is defined in `config/config.yaml`.  
   A pipeline consists of:
   - **Fetcher:** Reads data from a source.
   - **Writers:** Send or store data in the target destination.

2. **Execution Flow**  
   - The pipeline runner (`app.py`) reads the YAML configuration.
   - It loads fetchers and writers dynamically using `importlib`.
   - Data flows between components wrapped inside `DataWrapper`.

3. **Extensibility**  
   - Developers can add new fetchers/writers by extending the `Fetcher` or `Writer` interface.
   - No changes to the core system are required.

---

## Example Pipeline

### config.yaml
```yaml
pipeline:
  - name: "Docs to Sheets Pipeline"
    enabled: true

    fetcher:
      class: fetchers.doc_fetcher.DocsFetcher
      params:
        doc_id: "your-google-doc-id"
        service_name: "docs_cred"

    writers:
      - class: writers.sheet_writer.SheetsWriter
        params:
          sheet_id: "your-sheet-id"
          service_name: "sheets_cred"
        operation_params:
          mode: "append"
```


## Running the Pipeline

### Run with Config
```bash
python app.py
```

### List Operations
To list all available fetcher and writer operations for enabled pipelines:
```bash
python app.py --list-ops
```

### CLI Command (After Installation)
```bash
run-pipeline config/config.yaml
```

---

## Credential Management

All credentials are defined in `config/auth_config.yaml`.

Example:
```yaml
credentials:
  sheets_cred: "credentials/sheets.json"
  docs_cred: "credentials/docs.json"

scopes:
  google_sheets:
    - https://www.googleapis.com/auth/spreadsheets
  google_docs:
    - https://www.googleapis.com/auth/documents

bindings:
  sheets_cred:
    scope: google_sheets
  docs_cred:
    scope: google_docs
```

---

## Adding New Plugins

To add a new data source or destination:

1. Create a new Python file inside `fetchers/` or `writers/`.
2. Inherit from `Fetcher` (for fetchers) or `Writer` (for writers).
3. Implement required methods:
   - **Fetcher:** `fetch_data()` → returns `DataWrapper`
   - **Writer:** `write_data(data)` → processes `DataWrapper`
4. Add the new class to `config/config.yaml` using its fully-qualified path.

---

## Commands Summary

- **Run Pipeline:**  
  `python app.py --config config/config.yaml`
  
- **List Operations:**  
  `python app.py --list-ops --config config/config.yaml`

- **Install as CLI:**  
  `pip install -e .`  
  Then run:  
  `run-pipeline config/config.yaml`

---

## Key Components

- **Fetcher:** Fetches data from a source (Google Docs, Sheets, etc.).
- **Writer:** Writes or sends data to a destination (Sheets, Docs, etc.).
- **DataWrapper:** Standard data container with optional metadata.
- **Auth Utility:** Handles token-based and OAuth credentials.
- **Logger Utility:** Provides consistent logging across all components.

---
