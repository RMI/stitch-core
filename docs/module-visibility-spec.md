# Module visibility and import rules

## Scope and terms

These rules apply to all code under each distribution's `src/`, including public and private packages and their `__init__.py` modules. Tests follow the Tests section. Scripts and tooling outside `src/` are excluded.

Directives are required unless marked **should**. A **should** rule requires a reason for an exception.

- **Distribution:** a project configured for build in `pyproject.toml`. Each `src/` tree belongs to one distribution. Additional separately published packages must be uv workspace members.
- **Package root:** the top directory of a distribution's import namespace, such as `src/stitch/`.
- **Private name:** a module, package, or member name beginning with `_`.
- **Public name:** any other name.
- **Neighbour:** a module or package in the importer's directory, including that directory's `__init__.py`.
- **Published API:** names exposed for use outside the distribution.

## Visibility

**V1.** Import a private module or package only from its neighbours, except for the root `_internal` package.

**V2.** A private package may contain public modules and members.

**V3.** A module whose members are re-exported by its package **should** have a private name. Use public modules for code imported through the module's own path.

**V4.** Remove unused public members. Make a member private when it is used only within its defining module.

**V5.** Put code shared by distant modules in a public module or the root `_internal` package.

## Imports

**I1.** Use a single-dot relative import for neighbours, including paths through sibling packages. Use an absolute path from the package root otherwise. Never use two or more leading dots.

```python
# src/stitch/parent/baz.py
from ._foo import FooClass
from ._bar.sub_bar import sub_bar_func
from stitch._internal.app import AppContainer
```

**I2.** A private module or package name may appear only:

- first in a relative path; or
- as `_internal` immediately after the root package name.

**I3.** Do not import private members from other modules. You may import a private neighbour as a whole module; keep its local name private.

```python
from . import _utils
from . import _utils as _u
```

**I4.** Import members exposed by another package from that package, not its implementation modules.

**I5.** Put imports at the top of the module. The only allowed conditional imports are inside a top-level `if TYPE_CHECKING:` block, also at the top of the module. Resolve import cycles by changing dependencies or moving shared code.

## Depth

**L1.** Import paths **should** contain no more than two segments and must contain no more than four. Exclude the leading relative dot or absolute root package name. Count `_internal`.

For `from` imports, count only the path before `import`. For plain `import` statements, count the imported module path.

```python
from .app import operations                       # 1
from stitch._internal.app import AppContainer     # 2
from ._internal.app.operations import cut         # 3
```

**L2.** Limit directory depth to five, counting the package root as level one.

```text
src/<pkg>/a/b/c/d/__init__.py      # allowed: depth 5
src/<pkg>/a/b/c/d/e/__init__.py    # prohibited: depth 6
```

**L3.** Packages **should** contain many small modules rather than deeply nested subpackages.

## Declaring interfaces

**D1.** In `__init__.py`, define public members directly or re-export them. List every re-exported member in `__all__`.

```python
# src/stitch/_internal/app/__init__.py
from ._container import AppContainer

__all__ = ["AppContainer"]
```

**D2.** An ordinary module exposes its public definitions and intentional re-exports. Use `__all__` when needed to make that interface explicit.

## Internal code and published API

**A1.** A distribution may have one `_internal` package, directly under its package root. Do not create nested `_internal` packages.

**A2.** Any module in the distribution may import that `_internal` package, subject to the import rules.

**A3.** Declare the distribution's published API outside `_internal`, in public modules and package initializers. Define members there or re-export them from `_internal`.

**A4.** Provide public import paths for everything consumers need. Do not require consumers to import `_internal`.

## Tests

**T1.** Tests **should** import the published API.

**T2.** Tests may directly import a private module or package when it is the subject of the test.

**T3.** Tests **should** avoid importing private members.
