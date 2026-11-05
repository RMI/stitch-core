We leverage conventions to help specify clean interfaces and hide information.
Use `_` to prefix private symbols, packages, and modules.

Importing
Private modules or packages must explicitly declare their public exports at their top level through explicit declarations and/or `__all__ = []`.
Private packages must not export public namespaces
- Bad:
  ```
  example/src/example/
  
  ```
- Packages (`_internal_package/__init__.py`)
- not allowed:
    - `from .neighbor import _Foo`
    - `from my_package._private_module import Foo`
    - `from my_package.sub_package._private_module import Foo`
    - `from ._private_neighbor import _private_symbol`
- allowed:
    - `from ._private_neighbor.public_namespace`
- a module may use a relative import to import symbols from a private neighbor
    - allowed: `from ._private_module import PublicMember`


The `_internal` package is special. Only one can exist in a project, and it must be at the top of the package root `<repo root>/src/<package root>/_internal/`. It is the only private package that is allowed to export public namespaces.
 > Allowed: `._internal.typings`, `from ._internal.plugin.utils import register_plugin`
 
Within the `_internal` package, the rest of the import rules apply.

No importing of private symbols.
```python
# BAD
from some_package.file import _FileInternalClass
from .neighbor_module import _private_symbol
from .neighbor_module import _private_symbol as pub_symbol
from .neighbor_module.submod._sub_int import _sub_func
import .neighbor_module._private_symbol as pub_symbol

# GOOD
from some_package.file import FilePublicClass
from .neighbor_module import public_symbol
from ._private_neighbor_module import public_symbol
from ._private_neighbor_package.sub_mod import public_symbol, PublicClass
# see discussion of `_` prefixes in import statements below

# EXCEPTION!!!
# A private module/package may export many symbols that are often used together.
# In such cases, the following is allowed
from . import _utils
import ._utils as priv_utils
```

Private symbols (leading `_`) are ONLY allowed in the first segment of a relative import statement or the second if and only if the second segment is `_internal`.
```python
# BAD
from ._priv_pack.another._another_private import X`
import ._priv_pack._private_sub as aliased_public_sub`
from my_package._priv_pack.sub import sub_symbol`

# GOOD
from ._priv_pack.another.sub_a import Foo
import ._internal.app.operations.reading as read_ops
from my_package._internal.app.operations import reading
```

Symbols declared in an `__init__.py` module's `__all__` variable should be imported from the package and not namespaced.
Given the following:
```python
# _internal/app/operations.py

def transpose(...): ...

def cut(...): ...

@dataclass
class Op: ...
```

```python
# _internal/app/container.py

class AppContainer: ...
```

```python
# _internal/app/__init__.py

from .container import AppContainer

__all__ = ["AppContainer"]
```
- Note that `operations.py` is exposed as a namespace.
```python
# in _internal/registry.py

# BAD
from .app.container import AppContainer

# GOOD
from .app import AppContainer
from .app.operations import cut, Op # or from .app import operations as app_ops
```
```python
# in src/orchestration.py

# GOOD
from ._internal.app import AppContainer

# OK
import my_package._internal.app.operations as ops
```

Prefer relative imports for modules and packages that share the same parent directory.
```python
# in src/my_package/parent/baz.py

# BAD
from my_package.parent._foo import FooClass
from my_package.parent._bar.sub_bar import sub_bar_func, SUB_CONSTANT

# GOOD
from ._foo import FooClass
from ._bar.sub_bar import sub_bar_func, SUB_CONSTANT

# OK
from my_package._internal.internal_foo import InternalFooClass
```

Do not use relative import to reach beyond the parent directory.
```python
# in src/my_package/other_parent/child.py

# BAD
from ..parent.baz import Baz

# OK
from my_package.parent.baz import Baz
```
Prefer wide packages with many small modules to deeply nested packages with long namespaces.
Internal module and package namespacing is discouraged beyond 2 segments and not allowed beyond 4. That's often an indication that the boundaries aren't properly clarified.
- example: `from .neighbor.sub_a.sub_b import foo`
    - Is `neighbor` so large and complex that it needs 2 nested namespaces?
        - If so, perhaps `neighbor` can be decomposed into smaller elements, or `neighbor` may need to be moved to its own member package.
    - If `foo` is really part of the `neighbor` public interface, it may warrant moving to a less nested module.
    - Options:
        - move `foo` declaration to `neighbor/__init__.py`
        - make `sub_b` private and reexport from `sub_a/__init__.py`
- example: `from ._internal.app.domain.entities import Resource`
    - This implies `src/_internal/app/domain/entities.py` at minimum.
    - Are there so many modules and packages under `app/` and `domain/` that the directory structure is warranted?
    - Why not `app/entities.py`,  `_internal/domain/entities.py`, or `_internal/entities`?
