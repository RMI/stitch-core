# Module visibility enforcement

Tracks how each rule in [module-visibility-spec.md](module-visibility-spec.md) is checked.

Severity: **gate** fails `mise check`, **warn** is reported but passes, **manual** has no mechanical
check, **none** means the rule is permissive and there is nothing to check.

`mise check` depends on `lint` (ruff), `lint:imports` (ast-grep), `lint:structure`
(`scripts/check_layout.py`), and `typecheck` (ty). There is no pre-commit hook and no CI, so the
checks are voluntary until someone runs the task.

`_local/` (gitignored) holds two sample packages for exercising the rules by hand. Run
`ast-grep scan`, `ruff check .`, and `python ../../scripts/check_layout.py src/stitch.core` from inside
`_local/clean` or `_local/violations`. The clean tree passes all three; the violations tree fails
all three, and between them they cover every gated rule.

## Visibility

| Done | Rule | Spec | Enforced by | Severity |
| --- | --- | --- | --- | --- |
| [x] | V1 private module imported only by neighbours | must | ruff `TID252`, ast-grep `private-segment-position`, ast-grep `no-dynamic-private-import` | gate |
| [x] | V2 private package may hold public members | must | — | none |
| [ ] | V3 re-exported module should be private | should | — | manual |
| [ ] | V4 remove unused public members | must | — | manual |
| [x] | V5 shared code in a public module or `_internal` | must | V1 coverage | manual |

V1 falls out of I1 and I2 for every static import, so no import-graph tool is needed. The residual
case is a dynamic import, which `no-dynamic-private-import` covers.

V3 and V4 are dropped. Both need cross-module reachability that no available tool resolves
accurately, and a heuristic approximation produced more noise than signal on a library, where
"used" means "used by a consumer outside this repository".

## Imports

| Done | Rule | Spec | Enforced by | Severity |
| --- | --- | --- | --- | --- |
| [x] | I1 one dot for neighbours, absolute otherwise | must | ruff `TID252` (`ban-relative-imports = "parents"`), `check_layout` | gate |
| [x] | I2 private segment position | must | ast-grep `private-segment-position` | gate |
| [x] | I3 no private member imports | must | ast-grep `private-member-import`, ruff `SLF001` | gate |
| [x] | I4 import from the exposing package | must | `check_layout` | gate |
| [x] | I5 imports at top of module, none in functions or classes | must | ruff `PLC0415` and `E402`, ast-grep `conditional-import-placement` | gate |

ruff bans two or more leading dots. The "prefer relative for neighbours" half of I1 needs the
importing file's own path, so `check_layout` covers it. `SLF001` covers private attribute access,
not imports. `conditional-import-placement` closes the hole where a conditional import block sits
after other code, which neither `E402` nor `PLC0415` sees.

## Depth

| Done | Rule | Spec | Enforced by | Severity |
| --- | --- | --- | --- | --- |
| [x] | L1 import path depth | should <= 2 / must <= 4 | ast-grep `import-depth-preferred` and `import-depth-max` | warn > 2 / gate > 4 |
| [x] | L2 directory depth <= 5 | must | `check_layout` | gate |
| [ ] | L3 prefer many small modules | should | — | manual |

Gating L1 at two segments would make the spec's four-segment limit meaningless, so both thresholds
stand as written. L3 is dropped: the spec sets no threshold beyond L2, so there is nothing to check.

## Declaring interfaces

| Done | Rule | Spec | Enforced by | Severity |
| --- | --- | --- | --- | --- |
| [x] | D1 `__init__.py` re-exports in `__all__` | must | ruff `F401`, ast-grep `init-requires-all` and `no-redundant-alias-in-init` | gate |
| [x] | D2 ordinary module interface | must | ruff `F822`, `RUF022`, `RUF068`, `PLE0604`, `PLE0605` | gate |

The two ast-grep rules close the "no `__all__` at all" and `X as X` holes that `F401` leaves open
inside `__init__.py`. D2 is hygiene only; "use `__all__` when needed" stays a judgment call.
`RUF022` (sorted `__all__`) goes beyond the spec and is easy to drop.

## Internal code and published API

| Done | Rule | Spec | Enforced by | Severity |
| --- | --- | --- | --- | --- |
| [x] | A1 one `_internal`, directly under the root | must | `check_layout` | gate |
| [x] | A2 any module may import `_internal` | must | ast-grep I2 exception | none |
| [x] | A3 published API declared outside `_internal` | must | `check_layout` | gate |
| [x] | A4 public import paths for consumers | must | `check_layout` | gate |

A4 is checked only in part: every name in the root `__all__` must be bound in the root
`__init__.py`, which closes the hole where ruff suppresses `F822` inside `__init__.py`. The rest of
A4 is manual.

## Tests

| Done | Rule | Spec | Enforced by | Severity |
| --- | --- | --- | --- | --- |
| [x] | T1 tests import the published API | should | ast-grep `tests-prefer-public-api` | warn |
| [x] | T2 tests may import the private subject | may | scoped exemptions | none |
| [x] | T3 tests avoid private members | should | ast-grep `private-member-import`, ruff `SLF001` | gate |

T1 cannot be gated: T2 explicitly permits a test to import the private module it tests, so a hard
ban would contradict the spec. T2 holds because the `src/`-scoped ast-grep rules do not apply to
`tests/`.

T3 is promoted from **should** to a gate. Both tools take a per-case suppression comment carrying a
reason (`# noqa: SLF001  # reason`, `# ast-grep-ignore: private-member-import`), which is the
spec's own mechanism for a justified exception. This does not conflict with T2, which is about
private modules rather than private members.

A4 is likewise promoted to a gate, since a name in `__all__` that is not bound breaks
`from stitch.core import *` outright.

## Notes

- The ast-grep rules hard-code the root package name `stitch.core` in their regexes and `files` globs.
  Renaming the package root means updating `private-segment-position.yml`,
  `tests-prefer-public-api.yml`, and the `files` globs in the other rules.
- Tools: ruff, ty, pytest, and ast-grep.
