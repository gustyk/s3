"""Small crash-safe helpers for derived experiment artifacts."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any


def atomic_write_text(path: Path, content: str) -> None:
    """Write a UTF-8 artifact atomically within its destination directory."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8") as handle:
        handle.write(content)
        handle.flush()
        os.fsync(handle.fileno())
    temporary.replace(path)


def atomic_dataframe_csv(frame: Any, path: Path) -> None:
    """Atomically replace a derived CSV; ``frame`` is a pandas DataFrame."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    frame.to_csv(temporary, index=False)
    with temporary.open("r+b") as handle:
        os.fsync(handle.fileno())
    temporary.replace(path)
