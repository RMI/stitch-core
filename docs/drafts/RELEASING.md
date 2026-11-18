- releasing is manual

## Distinction between git tags and package version
There's no strict connection (yet) between the package version defined in `pyproject.toml` and `git` artifacts like tags. When publishing/releasing a package git tags and the release version have 2 distinct roles.

**package version**
This is the value under `project.version` in `pyproject.toml`. It's what dependency managers like `uv`, `poetry`, `pdm`, and `pip` use to actually resolve versions to satisfy the project configuration. So, when another application adds `rmi-stitch-core` as a dependency like `"rmi-stitch-core>=0.2.0,<0.3.0"`, that will only look in the configured index (PyPI by default) for the latest version that satisfies the constraints.

**git tags**
These only come into play around creating the GitHub releases (the `sdist` and `whl` files that are uploaded to GitHub). As of 2026-11-18, `uv` does not support dynamic versioning—where the **package version** is derived from VCS. There's nothing stopping us from calling `uv version 5.2.1 && git tag -am "release: 2.1.0" v3.2.1` and creating a GitHub release. Our tagged release on GitHub would be at `v3.2.1` that publishes `rmi-stitch-core@5.2.1`.


> [!INFO] Hatchling
> We can switch our build backend to [Hatchling](https://hatch.pypa.io/latest/), which offers [a plugin](https://github.com/ninoseki/uv-dynamic-versioning) to enable dynamic versioning in a `uv` project.
> As of 2026-11-18, we have not adopted dynamic versioning.

Given the separation, responsibility is ultimately on the developers to ensure that git tags and package versions are aligned.

Our current CI will publish to PyPI after a tagged release is created.

Rough process:
- commit changes & ensure git is clean
- update the package version
- commit
- tag the commit with the same version prefixed with "v"
- push the tag
- create a gh release from the tag

Scripts
- `version:bump <part>`
    - basically an alias for `uv version --bump <part> --no-sync`
- `version:set <version>`
    - like `bump`, alias for `uv version <version>`
- `version:commit`
    - assumes that at least `uv.lock` and `pyproject.toml` are changed/dirty
    - commits `pyproject.toml` and `uv.lock` with a standard message
- `git:tag` (probably rename to `version:tag`)
    - ensure git is clean
    - get the current uv version
    - create a tag from the current version
- `release:prepare <version part>`
    - ensure git is clean
    - run `version:bump <version part>`
    - run `version:commit`
    - run `git:tag`
- `release:publish`
    - no args
    - ensure git is clean
    - get the current declared version
    - ensure that the git tag corresponding to the version matches the current HEAD sha
        - could add an option here to stash, checkout the tag, and build from that commit
    - build the package
    - push the tag
    - create a GitHub release from the tag
