#!/usr/bin/env -S uv run --script
# MISE extends="py"
# MISE description = "Check module layout and visibility rules."

import ast
import sys
from collections.abc import Iterator
from pathlib import Path

MAX_DEPTH = 5


def mod(root: Path, file: Path) -> tuple[str, ...]:
    parts = file.relative_to(root.parent).with_suffix("").parts
    return parts[:-1] if parts[-1] == "__init__" else parts


def target_of(pkg: tuple[str, ...], node: ast.ImportFrom) -> tuple[str, ...]:
    base = pkg[: len(pkg) - node.level + 1] if node.level else ()
    return (*base, *node.module.split(".")) if node.module else base


def exported(tree: ast.Module) -> set[str] | None:
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        if any(getattr(t, "id", None) == "__all__" for t in node.targets):
            try:
                return set(ast.literal_eval(node.value))
            except ValueError:
                return set()
    return None


def bound(tree: ast.Module) -> set[str]:
    stores = (n for n in ast.walk(tree) if isinstance(n, ast.Name))
    names = {n.id for n in stores if isinstance(n.ctx, ast.Store)}
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef):
            names.add(node.name)
        elif isinstance(node, ast.Import | ast.ImportFrom):
            names |= {a.asname or a.name.split(".")[0] for a in node.names}
    return names


def check(root: Path) -> Iterator[str]:
    trees: dict[Path, ast.Module] = {
        f: ast.parse(f.read_text()) for f in sorted(root.rglob("*.py"))
    }
    inits: dict[Path, ast.Module] = {
        f: t for f, t in trees.items() if f.name == "__init__.py"
    }
    exports = {
        mod(root, f): a for f, t in inits.items() if (a := exported(t)) is not None
    }
    modules = {mod(root, f) for f in trees if f.name != "__init__.py"}

    dirs = (p for p in root.rglob("*") if p.is_dir() and p.name != "__pycache__")
    for d in sorted(dirs):
        depth = len(d.relative_to(root).parts) + 1
        if depth > MAX_DEPTH:
            yield f"{d}: L2 directory depth {depth} exceeds {MAX_DEPTH}"
        if d.name == "_internal" and d.parent != root:
            yield f"{d}: A1 `_internal` must sit directly under {root.name}"

    for file, tree in trees.items():
        here = mod(root, file)
        pkg = here if file.name == "__init__.py" else here[:-1]
        for node in ast.walk(tree):
            if not isinstance(node, ast.ImportFrom):
                continue
            target, at = target_of(pkg, node), f"{file}:{node.lineno}"
            if node.level == 0 and (target == pkg or target[:-1] == pkg):
                yield f"{at}: I1 `{node.module}` is a neighbour; use a relative import"
            owner = target[:-1]
            if target in modules and owner != here:
                shadowed = {a.name for a in node.names} & exports.get(owner, set())
                for name in sorted(shadowed):
                    yield f"{at}: I4 `{name}` is exposed by `{'.'.join(owner)}`"

    init = root / "__init__.py"
    if init not in trees:
        yield f"{root}: A3 missing __init__.py"
        return
    names, declared = bound(trees[init]), exports.get((root.name,))
    if declared is None and not any(not n.startswith("_") for n in names):
        yield f"{init}: A3 declare public members or `__all__` here"
    for name in sorted((declared or set()) - names):
        yield f"{init}: A4 `{name}` is in `__all__` but not bound here"


def main(argv: list[str]) -> int:
    findings = list(check(Path(argv[0]) if argv else Path("src/stitch")))
    print("\n".join(findings))
    return 1 if findings else 0


if __name__ == "__main__":
    print("running")
    raise SystemExit(main(sys.argv[1:]))
