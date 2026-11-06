# Module visibility and import rules

We use naming conventions to mark what is public and what is not, so that a
module's interface is visible from its name and from the way it is imported.
This document states the rules. A later section lists the checks we intend to
automate.

Rules marked **must** are errors. Rules marked **should** are strong
preferences that need a reason to break.

## Terms

- **Distribution**: a package configured for build in a `pyproject.toml`, either
  this repository's root project or a workspace member under `packages/`.
- **Package root**: the top directory of a distribution's import namespace, for
  example `src/stitch/`.
- **Private name**: a module, package, or symbol whose name starts with `_`.
- **Public name**: any other name.
- **Namespace module**: a module with a public name that callers import by its
  own path, rather than through its package's `__init__.py`.
- **Segment**: one dotted name written in an import statement, counted after the
  leading dots of a relative import or after the root package name of an
  absolute import. `from ._internal.app import X` is two segments.
- **Published API**: the names that code outside the distribution is meant to
  import.

## Scope

These rules bind all code under `src/`. Tests have a narrower rule of their own,
near the end. Scripts and tooling outside `src/` are not bound.

## 1. Visibility

1.1 A leading `_` means the name is not part of the surface its parent offers to
the rest of the codebase.

1.2 A private module or package **must** only be imported by modules that sit in
the same directory as it, including that directory's `__init__.py`. Nothing
further away may name it. `_internal` is the one exception, covered in section 5.

1.3 A private package may contain public modules and public symbols. Making a
package private restricts who may reach it, not what it may hold.

1.4 A module whose contents are re-exported by its package **should** have a
private name, so that the re-exported path is the only path that works.

```
_internal/app/_container.py     # re-exported through __init__.py
_internal/app/operations.py     # a namespace, imported by its own path
```

1.5 A public symbol inside a private package that no `__init__.py` ever
re-exports is either dead code or should be private. Fix it rather than leaving
it.

## 2. Where a name may be imported from

2.1 Use a relative import when the target sits in the importer's own directory.

2.2 Use an absolute import from the root package for everything else.

2.3 Never write two or more leading dots. A module does not reach up out of its
own directory by relative path.

```python
# in src/stitch/parent/baz.py
from ._foo import FooClass                  # same directory
from ._bar.sub_bar import sub_bar_func      # into a private sibling package
from stitch._internal.app import AppContainer

# BAD
from ..other.thing import Thing
from stitch.parent._foo import FooClass     # use the relative form
```

2.4 A module inside a private package imports its own neighbours relatively and
anything outside its directory by absolute path.

```python
# in src/stitch/parent/_bar/sub_bar.py
from . import sub_baz
from .sub_baz import helper
from stitch.parent.bar_sibling import Thing   # outside _bar, absolute
```

2.5 Because an absolute path may not contain a private segment (rule 3.1), a
module can never reach into a private package it does not live beside. That is
intended. If two distant modules need the same code, the code belongs in a
public module or under `_internal`.

## 3. How an import is written

3.1 A private segment **must** appear only in one of two positions:

- the first segment of a relative import, for example `from ._bar.sub import X`
- the segment `_internal` directly after the root package name, for example
  `from stitch._internal.app import X`

Anywhere else it is an error.

```python
# BAD
from ._priv_pack.another._another_private import X
from stitch._priv_pack.sub import sub_symbol
from stitch.sub_package._private_module import Foo

# GOOD
from ._priv_pack.another.sub_a import Foo
from stitch._internal.app.operations import cut
```

3.2 Never import a private symbol from another module, with or without an alias.

```python
# BAD
from stitch.file import _FileInternalClass
from .neighbor import _private_symbol
from .neighbor import _private_symbol as pub_symbol
```

3.3 One exception: a module may import a private neighbour as a whole module
when that neighbour exports many names used together. The local name **must**
keep a leading underscore, or the private module becomes a public attribute of
the importing module and leaks through it.

```python
# GOOD
from . import _utils
from . import _utils as _u

# BAD
from . import _utils as utils    # others could then write
                                 # from .this_module import utils
```

3.4 Import a re-exported symbol from the package, not from the module that
defines it. Rule 1.4 usually makes the deeper path illegal on its own.

```python
# _internal/app/__init__.py
from ._container import AppContainer

__all__ = ["AppContainer"]
```

```python
# in _internal/registry.py
from .app import AppContainer                  # GOOD
from .app.operations import cut, Op            # GOOD, operations is a namespace
from .app import operations as app_ops         # also fine

from .app._container import AppContainer       # BAD
```

3.5 Every import **must** sit at the top level of its module. Imports inside a
function or method body are not allowed. An import cycle is a sign that a
boundary is in the wrong place, so move the shared code rather than deferring
the import.

3.6 Depth. Count the segments written in the statement. More than two is
discouraged. More than four is an error.

```python
from ._internal.app import AppContainer            # 2
from ._internal.app.operations import cut          # 3, allowed, worth a look
from ._internal.app.domain.entities import Resource  # 4, allowed, usually wrong
```

A path of three or more segments is a question about structure. Is the package
large enough to deserve the nesting? Would the symbol be better placed in the
parent's `__init__.py`, or the subpackage better promoted to its own module?
Note that `_internal` counts as a segment, so a module two directories deep
inside the internal tree already reaches the discouraged level.

3.7 Prefer wide packages with many small modules over deep nesting with long
dotted paths.

## 4. Declaring a package surface

4.1 Every `__init__.py` **must** state its package's surface in one of two ways,
or both:

- declare the functions, classes, and constants directly in `__init__.py`
- list the re-exported names in `__all__`

A bare re-export statement is not a declaration. If `__init__.py` re-exports
anything, it carries an `__all__`.

```python
# stitch/app/__init__.py
from ._container import AppContainer
from ._engine import Engine

__all__ = ["AppContainer", "Engine"]
```

4.2 This duty is the same for public and private packages. Private packages are
not more explicit than public ones, they are only reachable from fewer places.

4.3 A plain module usually needs no `__all__`. Its surface is the set of public
names it declares. Add `__all__` when that is not clear enough.

## 5. The `_internal` package

5.1 A distribution may have at most one `_internal` package, directly beneath its
package root: `src/<root>/_internal/`. A package counts as a distribution only if
it is configured as one in a `pyproject.toml`. Today that is `stitch` alone.

```
src/stitch/_internal/                # OK
src/stitch/app/_internal/            # BAD, not at the package root
src/stitch/_internal/x/_internal/    # BAD, only one per distribution
```

5.2 `_internal` is optional. Create one when there is code to put in it.

5.3 It is the only private package that any module in its distribution may
import, by relative or absolute path.

```python
from stitch._internal.typings import Repository
from ._internal.app import AppContainer
import stitch._internal.app.operations as ops
```

5.4 Inside `_internal`, every rule in this document applies as normal.

## 6. The published API

6.1 The published API is what the public modules directly under the package root
expose, including `__init__.py`. Those modules either declare their names or
re-export them from `_internal`.

6.2 Code outside the distribution **must** never have to write `_internal` in an
import. Anything a consumer needs is reachable by a public path.

6.3 A type that appears in a public signature is part of the published API, even
if it is defined under `_internal`. Re-export it from a public module.

```python
# src/stitch/__init__.py
from ._internal.typings import Repository

__all__ = ["Repository", "connect"]
```

```python
# consumer code
from stitch import Repository, connect
```

## 7. Tests

7.1 Tests import the published API by default. A test that only uses public
paths is also a check that those paths work.

7.2 A test may import a private module or package directly when that module is
the subject of the test.

7.3 A test may import a private symbol, but this should be rare and deliberate.
It pins behaviour that is not a contract, so the test will break on refactors
that break nothing real.

```python
from stitch import connect                        # default
from stitch._internal import _utils               # fine when _utils is the subject
from stitch._internal._utils import _clamp        # rare
```

## 8. Checks to automate

These rules are written to be machine-checkable. Planned checks, roughly in
order of value:

- a private segment outside the two positions allowed by rule 3.1
- an import of a private symbol, rule 3.2
- a relative import with two or more leading dots, rule 2.3
- an import inside a function or method body, rule 3.5
- an `__init__.py` that re-exports without declaring `__all__`, rule 4.1
- a private module aliased to a public local name, rule 3.3
- more than four written segments as an error, more than two as a warning, rule 3.6
- a public symbol in a private package that nothing re-exports, rule 1.5
- a private package imported from outside its own directory, rule 1.2
- more than one `_internal` per distribution, or one not at the package root, rule 5.1
