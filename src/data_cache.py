"""Save/load PhreshPhish feature cache on disk."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


def cache_paths(data_dir: Path) -> dict[str, Path]:
    data_dir.mkdir(parents=True, exist_ok=True)
    return {
        "manifest": data_dir / "cache_manifest.json",
        "train_features": data_dir / "train_features.parquet",
        "test_features": data_dir / "test_features.parquet",
        "train_meta": data_dir / "train_meta.parquet",
        "test_meta": data_dir / "test_meta.parquet",
    }


def cache_config(
    train_sample_size: int,
    test_sample_size: int,
    max_html_chars: int,
) -> dict[str, int]:
    return {
        "train_sample_size": train_sample_size,
        "test_sample_size": test_sample_size,
        "max_html_chars": max_html_chars,
    }


def cache_is_valid(
    paths: dict[str, Path],
    config: dict[str, int],
    *,
    force_rebuild: bool = False,
) -> bool:
    if force_rebuild:
        return False
    needed = ("manifest", "train_features", "test_features", "train_meta", "test_meta")
    if not all(paths[k].exists() for k in needed):
        return False
    manifest = json.loads(paths["manifest"].read_text(encoding="utf-8"))
    return manifest == config


def load_from_disk(paths: dict[str, Path]) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    train_raw = pd.read_parquet(paths["train_meta"])
    test_raw = pd.read_parquet(paths["test_meta"])
    x_train_feat = pd.read_parquet(paths["train_features"])
    x_test_feat = pd.read_parquet(paths["test_features"])
    cols = {
        "url": "url",
        "html": "html",
        "label": "label",
        "date": "date" if "date" in train_raw.columns else None,
    }
    return train_raw, test_raw, x_train_feat, x_test_feat, cols


def save_to_disk(
    paths: dict[str, Path],
    train_raw: pd.DataFrame,
    test_raw: pd.DataFrame,
    x_train_feat: pd.DataFrame,
    x_test_feat: pd.DataFrame,
    cols: dict[str, Any],
    config: dict[str, int],
    data_dir: Path,
) -> None:
    meta_cols = [cols["url"], cols["label"], "label_bin"]
    if cols["date"] and cols["date"] in train_raw.columns:
        meta_cols.append(cols["date"])
    train_raw[meta_cols].to_parquet(paths["train_meta"], index=False)
    test_raw[meta_cols].to_parquet(paths["test_meta"], index=False)
    x_train_feat.to_parquet(paths["train_features"], index=False)
    x_test_feat.to_parquet(paths["test_features"], index=False)
    paths["manifest"].write_text(json.dumps(config, indent=2), encoding="utf-8")
    print(f"Saved cache to {data_dir}/")
