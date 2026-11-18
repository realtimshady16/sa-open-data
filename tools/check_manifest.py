#!/usr/bin/env python3
"""Check the tree against MANIFEST.json, and check MANIFEST.json against the tree.

Two failure modes, both silent until someone looks:

  1. a listed file's sha256 no longer matches  -> the record is not what it claims
  2. a data file exists that is not listed     -> the manifest has drifted behind the data

The second is why this script exists. Between v0.1.0 and v0.2.0 a whole dataset (the
crosswalk) was added and the manifest was not updated, so "every data file's sha256 is in
MANIFEST.json" was false while the checksum check still passed. A passing check is not a
complete check.

    python3 tools/check_manifest.py            # verify, report, exit 1 on any problem
    python3 tools/check_manifest.py --quiet    # exit code only
"""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "MANIFEST.json"

# Directories that hold data. A file here that is not in the manifest is an error.
DATA_DIRS = ["datasets"]
# Files that are data but deliberately excluded from the manifest (regenerable, or text).
EXCLUDE_SUFFIXES = {".md", ".py", ".json.bak"}
EXCLUDE_NAMES = {"README.md"}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    quiet = "--quiet" in sys.argv
    man = json.loads(MANIFEST.read_text())
    listed = {e["path"]: e for e in man["files"]}

    problems = []

    for path, entry in listed.items():
        p = ROOT / path
        if not p.exists():
            problems.append(f"missing:   {path}")
            continue
        actual = sha256(p)
        if actual != entry["sha256"]:
            problems.append(f"mismatch:  {path} (manifest {entry['sha256'][:12]}…)")
        size = p.stat().st_size
        if size != entry.get("bytes"):
            problems.append(f"size:      {path} ({size} ≠ {entry.get('bytes')})")

    on_disk = set()
    for d in DATA_DIRS:
        for p in (ROOT / d).rglob("*"):
            if not p.is_file():
                continue
            if p.name in EXCLUDE_NAMES or p.suffix in EXCLUDE_SUFFIXES:
                continue
            on_disk.add(str(p.relative_to(ROOT)))

    for path in sorted(on_disk - set(listed)):
        problems.append(f"unlisted:  {path}")

    if problems:
        if not quiet:
            print(f"{len(problems)} problem(s):")
            for line in problems:
                print("  " + line)
        return 1

    if not quiet:
        total = sum(e.get("bytes", 0) for e in man["files"])
        print(f"ok — {len(listed)} files, {total / 1e6:.1f} MB, all checksums and sizes match,")
        print(f"     and no data file under {', '.join(DATA_DIRS)}/ is unlisted.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
