"""
Environment configuration helpers.
Single source of truth: .env
"""

import base64
import json
import os
from typing import Any, Dict, Optional

from dotenv import load_dotenv


class EnvError(RuntimeError):
    """Raised when required environment variables are missing."""


ENV_SCHEMA: dict[str, dict[str, list[tuple[str, ...]] | list[str]]] = {
    "stub": {
        "required_all": [],
        "required_any": [],
    },
    "live": {
        "required_all": ["EXA_API_KEY", "TAVILY_API_KEY"],
        "required_any": [("GOOGLE_API_KEY", "GEMINI_API_KEY")],
    },
}


def load_env() -> None:
    """Load .env once per process; no override for already-exported vars."""
    load_dotenv(override=False)


def get_env(key: str, default: Optional[str] = None) -> Optional[str]:
    load_env()
    return os.getenv(key, default)


def get_env_required(key: str) -> str:
    """Get an env var or raise a hard error when missing."""
    value = get_env(key)
    if value:
        return value
    raise EnvError(f"Missing required env: {key}")


def validate_env(mode: str = "stub") -> list[str]:
    """
    Validate required env keys for a runtime mode.
    Returns a list of missing requirements; empty list means valid.
    """
    load_env()
    if mode not in ENV_SCHEMA:
        raise EnvError(f"Unknown env validation mode: {mode}")

    schema = ENV_SCHEMA[mode]
    missing: list[str] = []

    for key in schema["required_all"]:
        if not os.getenv(key):
            missing.append(key)

    for group in schema["required_any"]:
        if not any(os.getenv(key) for key in group):
            missing.append(" | ".join(group))

    return missing


def get_google_api_key() -> Optional[str]:
    """
    Backward-compatible API key resolution.
    Prefer GOOGLE_API_KEY, fallback to GEMINI_API_KEY.
    """
    return get_env("GOOGLE_API_KEY") or get_env("GEMINI_API_KEY")


def _read_service_account_from_json(raw: str) -> Optional[Dict[str, Any]]:
    try:
        data = json.loads(raw)
        if isinstance(data, dict) and data.get("type") == "service_account":
            return data
    except Exception:
        return None
    return None


def get_gcp_service_account_info() -> Optional[Dict[str, Any]]:
    """
    Resolve Google service account from .env.
    Supported keys (priority order):
    1) GCP_SERVICE_ACCOUNT_JSON_B64
    2) GCP_SERVICE_ACCOUNT_JSON
    3) GCP_SERVICE_ACCOUNT_* split variables
    """
    load_env()

    raw_b64 = os.getenv("GCP_SERVICE_ACCOUNT_JSON_B64")
    if raw_b64:
        try:
            decoded = base64.b64decode(raw_b64).decode("utf-8")
            parsed = _read_service_account_from_json(decoded)
            if parsed:
                return parsed
        except Exception:
            pass

    raw_json = os.getenv("GCP_SERVICE_ACCOUNT_JSON")
    if raw_json:
        parsed = _read_service_account_from_json(raw_json)
        if parsed:
            return parsed

    fields = {
        "type": os.getenv("GCP_SERVICE_ACCOUNT_TYPE"),
        "project_id": os.getenv("GCP_PROJECT_ID"),
        "private_key_id": os.getenv("GCP_PRIVATE_KEY_ID"),
        "private_key": os.getenv("GCP_PRIVATE_KEY"),
        "client_email": os.getenv("GCP_CLIENT_EMAIL"),
        "client_id": os.getenv("GCP_CLIENT_ID"),
        "auth_uri": os.getenv("GCP_AUTH_URI"),
        "token_uri": os.getenv("GCP_TOKEN_URI"),
        "auth_provider_x509_cert_url": os.getenv("GCP_AUTH_PROVIDER_X509_CERT_URL"),
        "client_x509_cert_url": os.getenv("GCP_CLIENT_X509_CERT_URL"),
    }

    if not all(fields.values()):
        return None

    fields["private_key"] = str(fields["private_key"]).replace("\\n", "\n")
    return fields
