"""Lightweight .env loader (no external dependency)."""

from __future__ import annotations

from pathlib import Path
import os


def _parse_line(raw: str) -> tuple[str, str] | None:
    line = raw.strip()
    if not line or line.startswith("#"):
        return None
    if line.startswith("export "):
        line = line[len("export ") :].strip()
    if "=" not in line:
        return None
    key, _, value = line.partition("=")
    key = key.strip()
    value = value.strip()
    if not key:
        return None
    if value and value[0] in {"'", '"'} and value[-1:] == value[:1]:
        value = value[1:-1]
    return key, value


def load_env_file(path: str | Path, *, override: bool = False) -> dict[str, str]:
    env_path = Path(path)
    if not env_path.exists():
        return {}
    loaded: dict[str, str] = {}
    for raw in env_path.read_text(encoding="utf-8").splitlines():
        parsed = _parse_line(raw)
        if not parsed:
            continue
        key, value = parsed
        if override or key not in os.environ:
            os.environ[key] = value
        loaded[key] = value
    return loaded


def load_env(*, override: bool = False) -> dict[str, str]:
    candidates = [
        Path.cwd() / ".env",
        Path(__file__).resolve().parents[3] / ".env",
    ]
    loaded: dict[str, str] = {}
    for path in candidates:
        loaded.update(load_env_file(path, override=override))
    return loaded


__all__ = ["load_env", "load_env_file"]
