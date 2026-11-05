## `build`

- **Usage:** `build`

Build `stitch-core` python package.

## `check`

- Depends: lint, typecheck

- **Usage:** `check`

Lint and typecheck.

## `format`

- **Usage:** `format`

Run the ruff formatter.

## `gh:release`

- **Usage:** `gh:release`

Build and publish the version tagged at HEAD

## `git:tag`

Tag the current version, optionally bumping first


- **Usage:** `git:tag [-b --bump <part>] [version]`
- **Aliases:** `gt`

### Arguments
- **`[version]`** — (Optional) set the version before tagging.

### Flags
- **`-b --bump <part>`**

  **Choices:** `major`, `minor`, `patch`

## `lint`

- **Usage:** `lint`

Run the ruff linter.

## `test`

- **Usage:** `test`

Run unit tests with pytest

## `typecheck`

- **Usage:** `typecheck`

Run the `ty` type checker.

## `version:bump`

Bump the shared version and commit


- **Usage:** `version:bump <part>`
- **Aliases:** `v:b`

### Arguments
- **`<part>`**

  **Choices:** `major`, `minor`, `patch`

## `version:set`

Set version numbers for packages. Sets all member packages if `--package` not passed.


- **Usage:** `version:set [-p --package <pkg>] <version>`
- **Aliases:** `vset`

### Arguments
- **`<version>`** — The full version to set.

### Flags
- **`-p --package <pkg>`** — The name of the package to set.

## `workspace:packages`

- **Usage:** `workspace:packages`
- **Aliases:** `ws:pkg`

List workspace package names, including the root
