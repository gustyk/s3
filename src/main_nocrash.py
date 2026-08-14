"""Deprecated alias; the unified runner now provides atomic output and explicit failures."""

from src.experiment import main

if __name__ == "__main__":
    raise SystemExit(main())
