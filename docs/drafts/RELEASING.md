# Releasing Packages

## Overview
Broadly speaking, `stitch-core` uses a tagged release process to publish the distribution to both PyPI and GitHub. We manually create tagged releases on GitHub; this triggers a workflow that publishes the release assets to PyPI.

### Distinction between git tags and package version
There's no strict connection (yet) between the package version defined in `pyproject.toml` and `git` artifacts like tags. When publishing/releasing a package git tags and the release version have 2 distinct roles.

**package version**
This is the value under `project.version` in `pyproject.toml`. It's what dependency managers like `uv`, `poetry`, `pdm`, and `pip` use to actually resolve versions to satisfy the project configuration. So, when another application adds `rmi-stitch-core` as a dependency like `"rmi-stitch-core>=0.2.0,<0.3.0"`, that will only look in the configured index (PyPI by default) for the latest version that satisfies the constraints.

**git tags**
These only come into play around creating the GitHub releases (the `sdist` and `whl` files that are uploaded to GitHub). As of 2026-11-18, `uv` does not support dynamic versioning—where the **package version** is derived from VCS. There's nothing stopping us from calling `uv version 5.2.1 && git tag -am "release: 2.1.0" v3.2.1` and creating a GitHub release. Our tagged release on GitHub would be at `v3.2.1` that publishes `rmi-stitch-core@5.2.1`.


> [!INFO] Hatchling
> We can switch our build backend to [Hatchling](https://hatch.pypa.io/latest/), which offers [a plugin](https://github.com/ninoseki/uv-dynamic-versioning) to enable dynamic versioning in a `uv` project.
> As of 2026-11-18, we have not adopted dynamic versioning.

Given the separation, responsibility is ultimately on the developers to ensure that git tags and package versions are aligned.

## Versioning
- The **package version** is the source of truth!
- Don't create version tags (`"vX.X.X"`) manually, use the scripts.
- It's not strictly necessary to create tags whenever the **package version** is changed.
- It is important to keep changes to the package version committed in isolated commits.

Given the manual process, we're free to create releases whenever we desire. So we can develop and merge as normal until we choose to create a release. It's important to note that updating the **package version** leads to changes in `pyproject.toml` and `uv.lock` that need to be committed. It's recommended to create an isolated commit when bumping the **package version**

### Create a release from existing version
- assumes no corresponding tag exists for the **package version**
    - e.g. latest tagged release is `v0.2.0` and current **package version** is `0.3.1`
- checkout `main`
- create the tag `v0.3.1`
- push the tag
- create a GitHub release from the tag
- This process can also be run from a specific commit hash. So if latest tag is at `v0.2.0` and current **package version** is `0.3.1`
    - let's say the **package version** was bumped to 0.3.1 in `HEAD~2`
    - checkout `HEAD~3` first, confirm **package version** is `0.3.0`
    - run through the above steps to tag and release `v0.3.0`

### Create a new release
#### Pre-releases
These are more straightforward as the expectation is that they generally won't be fetched unless explicitly requested.
```bash
# update the package version
uv version --bump minor --bump dev # creates the next dev version 1.2.0 -> 1.3.0.dev1

# commit `pyproject.toml` and `uv.lock`
git commit --only -m "chore(release): v$(uv version --short)" -- pyproject.toml uv.lock

# create and push the tag
git tag -a "v1.3.0.dev1" -m "Release v1.3.0.dev1"  
git push origin "refs/tags/$tag"

# create the release

```
This applies to situations where the **package version** hasn't been updated.
- pre-release -> stable
- stable with existing tagged release -> new stable

## Release Scenarios
These are the common situations where a developer may want to publish a release.
- working on a new feature -> create pre-releases
- features are merged and **package version** is unchanged
    - work has been happening but there's an existing tagged release that matches the current package version
    - either delete existing releases and update the tag
    - or cut a new `release/` branch with the new version, create new tagged release after merge
        - we allow tag pushes to `main`, but not other changes
- features are merged and **package version** is changed
    - no tagged release exists for the current package version
    - create and push the tag from the version
    - create the release from the tag
%%Seems like the general guidance is to not create tags while developing. That leads to some hassle when creating a release%%


Rough process:
- commit changes & ensure git is clean
- update the package version
- commit
- tag the commit with the same version prefixed with "v"
- push the tag
- create a gh release from the tag

More detail:
- First, briefly think about the eventual target version
    - breaking/changing the API of the package? => major
    - adding something new? => minor
    - refactoring, dependency updates, docs, tests, bug fixes? => patch
- once the target version is specified, we then need to determine if pre-releases are necessary
    - mostly determined by the scope of change
    - bugs and hotfixes for a patch release? probably no need for `dev`, `alpha`, `rc`, etc...
    - larger feature additions? (major/minor) probably yes
    - pre-release versions can be thought of as segmenting work into smaller steps
    - for any pre-release, you target the **next** version, followed by the identifier
        - say we're currently at `1.1.1`
        - pre-releases for `1.1.2` are `1.2.2.[dev|rc|b|a]#`
        - pre-releases for `1.2.0` are `1.2.0.[dev|rc|b|a]#`
        - pre-releases for `2.0.0` are `2.0.0.[dev|rc|b|a]#`
- with the next version

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

Troubleshooting
- git tag and package version mismatch
- releasing without a tag?
- erroneous tag released (e.g. created a tagged release but the repo is faulty)
    - should prevent this with branch protections
- How to delete a release (kinda the nuclear option, but if anything is wrong with a release):
    - delete from PyPI: login, navigate to project > releases, select "delete" in Options dropdown
    - delete from GitHub
- How to reset a tag