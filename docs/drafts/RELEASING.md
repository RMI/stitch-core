# Releasing Packages

## Overview <!-- section 1. -->
Broadly speaking, `stitch-core` uses a tagged release process to publish the distribution to both PyPI and GitHub. We manually create tagged releases on GitHub; this triggers a workflow that publishes the release assets to PyPI.

### Distinction between git tags and package version <!-- section 2. -->
There's no strict connection (yet) between the package version defined in `pyproject.toml` and `git` artifacts like tags. When publishing/releasing a package git tags and the release version have 2 distinct roles.

**package version**
This is the value under `project.version` in `pyproject.toml`. It's what dependency managers like `uv`, `poetry`, `pdm`, and `pip` use to actually resolve versions to satisfy the project configuration. So, when another application adds `rmi-stitch-core` as a dependency like `"rmi-stitch-core>=0.2.0,<0.3.0"`, that will only look in the configured index (PyPI by default) for the latest version that satisfies the constraints.

**git tags**
These only come into play around creating the GitHub releases (the `sdist` and `whl` files that are uploaded to GitHub). As of 2026-11-18, `uv` does not support dynamic versioning—where the **package version** is derived from VCS. There's nothing stopping us from calling `uv version 5.2.1 && git tag -am "release: 2.1.0" v3.2.1` and creating a GitHub release. Our tagged release on GitHub would be at `v3.2.1` that publishes `rmi-stitch-core@5.2.1`.

Given the separation, responsibility is ultimately on the developers to ensure that git tags and package versions are aligned.

## Versioning <!-- section 3 -->
- The **package version** is the source of truth!
- Don't create version tags (`"vX.X.X"`) manually, use the scripts.
- It's not strictly necessary to create tags whenever the **package version** is changed.
- It is important to keep changes to the package version committed in isolated commits.
- Rules permit developers to push `v*` tags
- As of 2026-11-18, we recommend only bumping major, minor, patch, and the `dev` pre-release version segment

Given the manual process, we're free to create releases whenever we desire. So we can develop and merge as normal until we choose to create a release. It's important to note that updating the **package version** leads to changes in `pyproject.toml` and `uv.lock` that need to be committed. It's recommended to create an isolated commit when bumping the **package version**

## Releasing <!-- sections 5 and 6 -->

Our CI automatically publishes to PyPI when a release is created, so assume that the release process implicitly covers PyPI.

### Release Scenarios <!-- section 5. -->
There are 2 primary scenarios where you may want to create a release. Basically, its whether the current package version matches an existing tagged release or not.
1. Features are merged in a branch (incl. `main`) and **package version** is unchanged
    - **package version** matches a release tag.
    - if the release is erroneous and should be replaced/overridden, see [[#Troubleshooting 7. Recovery]]
    - otherwise see [[#Create a new release]]
2. Features are merged in a branch and **package version** is changed
    - **package version** does not match a release tag.
    - no tagged release exists for the current package version
    - see [[#Create a release from existing version]]

### Create a release from existing version <!-- section 6.1 -->
<!-- TODO: add script details -->
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

### Create a new release <!-- section 6.2 -->
<!-- TODO: add script details for both -->

#### Pre-releases
<!-- covers stable -> pre-release for next stable -->
These are more straightforward as the expectation is that they generally won't be fetched unless explicitly requested.
```bash
# update the package version
uv version --bump minor --bump dev # creates the next dev version 1.2.0 -> 1.3.0.dev1

# commit `pyproject.toml` and `uv.lock`
git commit --only -m "chore(release): v$(uv version --short)" -- pyproject.toml uv.lock

# create and push the tag
git tag -a "v1.3.0.dev1" -m "Release v1.3.0.dev1"  
git push origin "refs/tags/v1.3.0.dev1"

# create the release

```

#### Stable Releases
<!-- covers stable to next stable and pre-release to stable -->
- cut a new `release/` branch with the new version, create new tagged release after merge

## Troubleshooting and Recovery <!-- section 7. -->
- git tag and package version mismatch
- releasing without a tag?
- erroneous tag released (e.g. created a tagged release but the repo is faulty)
- How to delete a release (kinda the nuclear option, but if anything is wrong with a release):
    - delete from PyPI: login, navigate to project > releases, select "delete" in Options dropdown
    - delete from GitHub
- How to reset a tag