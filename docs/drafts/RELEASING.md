# Releasing Packages

## Overview <!-- section 1. -->
Broadly speaking, `stitch-core` uses a tagged release process to publish the distribution to both PyPI and GitHub. We manually create tagged releases on GitHub; this triggers a workflow that publishes the release assets to PyPI. This document outlines the rules and procedures around our release process and is intended to help mitigate erroneous releases and make the process reasonably straightforward for maintainers.

### Distinction between git tags and package version <!-- section 2. -->
There's no strict connection between the package version defined in `pyproject.toml` and `git` artifacts like tags. When publishing/releasing a package git tags and the **package version** have 2 distinct roles.

**package version**
This is the value under `project.version` in `pyproject.toml`. It's what dependency managers like `uv`, `poetry`, `pdm`, and `pip` use to actually resolve versions to satisfy the project configuration. So, when another application adds `rmi-stitch-core` as a dependency like `"rmi-stitch-core>=0.2.0,<0.3.0"`, existing packaging tools search the configured index (PyPI by default) for the latest **package version** that satisfies the constraints.

**git tags**
Git tags serve 2 purposes when releasing: targets for creating GitHub releases and for selecting the commit when publishing to PyPI. As of 2026-11-18, `uv` does not support dynamic versioning—where the **package version** is derived from VCS. There's nothing stopping us from calling `uv version 5.2.1 && git tag -am "release: 2.1.0" v3.2.1` and creating a GitHub release. Our tagged release on GitHub would be at `v3.2.1` that publishes `rmi-stitch-core@5.2.1`.

## Versioning <!-- section 3 -->

Our main goal is to ensure that git version tags always align with a corresponding **package version**.
- Tag names match the **project version**: `"v<project version>`.
- Tags point to commits where `pyproject.toml` contains that version.

> [!IMPORTANT] Developer Responsibility
> Given the separation described above, responsibility is ultimately on the developers to ensure that git tags and package versions are aligned.

- The **package version** is the source of truth! Tags are derived from the **package version**.
- Don't create version tags (`"vX.X.X"`) manually, use the scripts.
- Branch protection rules permit developers to push `v*` tags
- It's not strictly necessary to create tags whenever the **package version** is changed.
- As of 2026-11-18, we only use major, minor, patch, and the `dev` pre-release version segment

Given the manual process, we're free to create releases whenever we desire. So we can develop and merge as normal until we choose to create a release. It's important to note that updating the **package version** leads to changes in `pyproject.toml` and `uv.lock` that need to be committed. It's recommended to create an isolated commit when bumping the **package version**.

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
This option assumes that no corresponding tag exists for the **package version**—e.g. latest tagged release is `v0.2.0` and current **package version** is `0.3.1`.
```bash
# checkout main branch
git checkout main 

# create new tag from `pyproject.toml` version
mise run git:tag

# push the tag, build, and create a release
mise run release:publish
```

> [!NOTE] Using a different branch or commit
> This process can also be run from a different branch or specific commit hash. So given
> - latest tag is at `v0.2.0`
> - current **package version** is `0.3.1`
> - the **package version** was bumped to `0.3.1` in `HEAD~2`
> 
> You can run
> ```bash
> # from main
>  git checkout HEAD~3
>  mise run git:tag
>  mise run release:publish
> ```

### Create a new release <!-- section 6.2 -->

#### Pre-releases
These are more straightforward as the expectation is that they generally won't be fetched unless explicitly requested.
```bash
# checkout feature branch
git checkout -b feat/new-feature

# update the version
mise run version:bump minor dev # creates the next dev version 1.2.0 -> 1.3.0.dev1

# commit `pyproject.toml` and `uv.lock`
mise run version:commit

# create the tag
mise run git:tag

# create the release
mise run release:publish
```
A shorter option which does the same thing:
```bash
git checkout -b feat/new-feature
mise run release:prepare minor dev # bump, commit, & tag
mise run release:publish
```

#### Stable Releases

> [!NOTE] "Stable"
> Stable releases are any version that only comprises the major, minor, and patch segments.

When moving between stable releases (e.g. `0.2.1 -> 0.2.2`, `1.0.1 -> 1.2.0`)
```bash
# create new branch with the target release
# current version is 1.0.1
git checkout -b release/1.2.0

mise run version:bump minor # bump to 1.2.0
mise run version:commit

git push

# create PR for release/1.2.0 -> main

# after PR merged
git checkout main
git pull
mise run git:tag
mise run release:publish
```

When moving from pre-release to stable (e.g. `0.2.0.dev6 -> 0.2.0`). 
```bash
# curent version is at 0.2.0.dev6
git checkout -b release/0.2.0 

mise run version:bump stable # `uv version` convenience
mise run version:commit

# remaining steps same as above 
```

## Troubleshooting and Recovery <!-- section 7. -->
> TBD
<!-- Working Notes
- git tag and package version mismatch
- releasing without a tag?
- erroneous tag released (e.g. created a tagged release but the repo is faulty)
- How to delete a release (kinda the nuclear option, but if anything is wrong with a release):
    - delete from PyPI: login, navigate to project > releases, select "delete" in Options dropdown
    - delete from GitHub
- How to reset a tag
-->