"""Check that a clean rerun reproduced the committed CSV outputs.

Run from the repository root after Restart & Run All on notebooks 01-05:

    python tools/check_rerun_outputs.py

Every CSV under data/ and outputs/ is compared with its last committed
version (git HEAD). Text values must match exactly. Numbers must match to
within a relative tolerance of 1e-9, because rerunning the optimizer can
change only the last few decimal places (for example 273.33325032094683
vs 273.333250320947).
"""
import io
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

RTOL = 1e-9
ATOL = 1e-9


def committed_version(path):
    result = subprocess.run(["git", "show", f"HEAD:{path.as_posix()}"],
                            capture_output=True)
    if result.returncode != 0:
        return None
    return pd.read_csv(io.BytesIO(result.stdout))


def compare(path):
    old = committed_version(path)
    if old is None:
        return "NEW (not in last commit, skipped)"
    new = pd.read_csv(path)
    if list(old.columns) != list(new.columns) or old.shape != new.shape:
        return f"DIFFERENT shape or columns: {old.shape} -> {new.shape}"
    for col in old.columns:
        a, b = old[col], new[col]
        if pd.api.types.is_numeric_dtype(a) and pd.api.types.is_numeric_dtype(b):
            ok = np.isclose(a.to_numpy(float), b.to_numpy(float),
                            rtol=RTOL, atol=ATOL, equal_nan=True)
            if not ok.all():
                row = int(np.argmin(ok))
                return f"DIFFERENT in '{col}' (row {row + 2}): {a.iloc[row]} -> {b.iloc[row]}"
        elif not a.astype(str).equals(b.astype(str)):
            return f"DIFFERENT text in '{col}'"
    return "identical"


def main():
    files = sorted(p for folder in ("data", "outputs")
                   for p in Path(folder).rglob("*.csv"))
    results = [(p, compare(p)) for p in files]
    width = max(len(p.as_posix()) for p, _ in results)
    for p, status in results:
        print(f"{p.as_posix():<{width}}  {status}")
    new = [p for p, s in results if s.startswith("NEW")]
    changed = [p for p, s in results if s not in ("identical",) and not s.startswith("NEW")]
    checked = len(files) - len(new)
    print()
    print(f"{checked} committed CSV files checked: {checked - len(changed)} identical, "
          f"{len(changed)} changed (numeric tolerance {RTOL:g}).")
    if new:
        print(f"{len(new)} new CSV file(s) not in the last commit were skipped.")
    sys.exit(1 if changed else 0)


if __name__ == "__main__":
    main()
