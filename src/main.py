"""Backward-compatible entry point for the auditable experiment runner."""

from src.experiment import main

if __name__ == "__main__":
    raise SystemExit(main())
