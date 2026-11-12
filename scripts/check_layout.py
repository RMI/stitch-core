import sys
from pathlib import Path

MAX_DEPTH = 5
root = Path(sys.argv[1])
errors = []

for directory in sorted(root.rglob("*")):
    if not directory.is_dir() or "__pycache__" in directory.parts:
        continue

    if len(directory.relative_to(root).parts) + 1 > MAX_DEPTH:
        errors.append(f"{directory}: directory depth exceeds {MAX_DEPTH}")

    if directory.name == "_internal" and directory.parent != root:
        errors.append(f"{directory}: _internal must sit directly under {root}")

if errors:
    print("\n".join(errors))
    sys.exit(1)
