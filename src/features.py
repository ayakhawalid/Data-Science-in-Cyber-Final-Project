"""URL and HTML feature extraction for phishing detection."""

from __future__ import annotations

import re
from typing import Any
from urllib.parse import urlparse

import pandas as pd

SUSPICIOUS_URL_TOKENS = (
    "login",
    "signin",
    "verify",
    "secure",
    "account",
    "update",
    "bank",
    "wallet",
    "confirm",
)


def extract_url_features(url: str) -> dict[str, Any]:
    """Extract lexical URL features used in phishing detection literature."""
    url = url or ""
    parsed = urlparse(url)
    host = parsed.netloc or ""
    path = parsed.path or ""

    return {
        "url_length": len(url),
        "host_length": len(host),
        "path_length": len(path),
        "num_dots": url.count("."),
        "num_hyphens": url.count("-"),
        "num_digits": sum(ch.isdigit() for ch in url),
        "num_subdomains": max(host.count(".") - 1, 0),
        "uses_https": int(parsed.scheme.lower() == "https"),
        "has_at_symbol": int("@" in url),
        "has_ip_host": int(bool(re.match(r"^\d{1,3}(\.\d{1,3}){3}", host))),
        "suspicious_token_count": sum(
            1 for token in SUSPICIOUS_URL_TOKENS if token in url.lower()
        ),
    }


def extract_html_features(html: str) -> dict[str, Any]:
    """Extract simple structural HTML features (no browser rendering)."""
    html = html or ""
    lower = html.lower()

    return {
        "html_length": len(html),
        "num_forms": lower.count("<form"),
        "num_inputs": lower.count("<input"),
        "num_password_inputs": lower.count('type="password"')
        + lower.count("type='password'"),
        "num_scripts": lower.count("<script"),
        "num_links": lower.count("<a "),
        "num_iframes": lower.count("<iframe"),
        "has_password_field": int(
            'type="password"' in lower or "type='password'" in lower
        ),
    }


def build_feature_dataframe(df: pd.DataFrame, url_col: str, html_col: str) -> pd.DataFrame:
    """Build a tabular feature matrix from raw URL and HTML columns."""
    url_features = df[url_col].fillna("").map(extract_url_features).apply(pd.Series)
    html_features = df[html_col].fillna("").map(extract_html_features).apply(pd.Series)
    return pd.concat([url_features, html_features], axis=1)
