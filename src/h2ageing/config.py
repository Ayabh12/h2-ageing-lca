"""Configuration: load a YAML file, apply command-line overrides, resolve paths."""
from __future__ import annotations

import copy
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]          # repository root
DEFAULT_CONFIG = ROOT / "config" / "default.yaml"


def load_config(path: str | Path | None = None, overrides: list[str] | None = None) -> dict:
    """Read a YAML configuration and apply overrides of the form ``a.b.c=value``.

    Values in overrides are parsed with YAML, so ``3``, ``3.0``, ``[6, 14]`` and
    ``linear`` all get the expected type.
    """
    path = Path(path) if path else DEFAULT_CONFIG
    with open(path, encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    for item in overrides or []:
        key, _, raw = item.partition("=")
        if not _:
            raise ValueError(f"override must look like key.sub=value, got {item!r}")
        set_value(cfg, key.strip(), yaml.safe_load(raw))
    return cfg


def set_value(cfg: dict, dotted: str, value) -> None:
    node = cfg
    keys = dotted.split(".")
    for k in keys[:-1]:
        if k not in node:
            raise KeyError(f"unknown configuration key: {dotted}")
        node = node[k]
    if keys[-1] not in node:
        raise KeyError(f"unknown configuration key: {dotted}")
    node[keys[-1]] = value


def with_values(cfg: dict, **dotted_values) -> dict:
    """Return a copy of ``cfg`` with some values changed: ``with_values(cfg, **{"usage.compression_kWh_per_kg": 3})``."""
    new = copy.deepcopy(cfg)
    for k, v in dotted_values.items():
        set_value(new, k, v)
    return new


def resolve(path: str | Path) -> Path:
    """Paths in the configuration are relative to the repository root."""
    p = Path(path)
    return p if p.is_absolute() else ROOT / p
