import yaml
import json
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.service_account import Credentials as ServiceAccountCredentials

def get_credentials(service_name, config_file="auth_config.yaml"):
    # Load YAML config
    with open(config_file, "r") as f:
        config = yaml.safe_load(f)

    credentials_map = config.get("credentials", {})
    scopes_map = config.get("scopes", {})
    bindings_map = config.get("bindings", {})

    if service_name not in credentials_map:
        raise ValueError(f"Credential '{service_name}' not found in config")

    cred_path = credentials_map[service_name]

    if service_name not in bindings_map:
        raise ValueError(f"Binding for '{service_name}' not found in config")

    scope_key = bindings_map[service_name].get("scope")
    if not scope_key or scope_key not in scopes_map:
        raise ValueError(f"Scope '{scope_key}' for '{service_name}' not found in config")

    # scopes = [scopes_map[scope_key]]
    scopes = scopes_map[scope_key]
    if not isinstance(scopes, list):
        scopes = [scopes]


    # Detect credential type (service account vs OAuth client)
    with open(cred_path, "r") as f:
        info = json.load(f)

    if info.get("type") == "service_account":
        # Service account credentials
        creds = ServiceAccountCredentials.from_service_account_file(cred_path, scopes=scopes)
    else:
        # OAuth client ID flow (user consent)
        flow = InstalledAppFlow.from_client_secrets_file(cred_path, scopes=scopes)
        creds = flow.run_local_server(port=0)

    return creds
