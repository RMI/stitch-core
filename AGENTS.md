# AGENTS.md

## Role

- Work as a general collaborator: implement, debug, and refactor on request.
- Keep designs and code brief and simple. Solve the current task only.

## Control

- Push or open pull requests only when the user asks.
- Ask before you cut a release or change the version, including the `release:*`, `version:*`, and `git:tag` mise tasks.
- Ask before you change the public API: exported names, signatures, or model fields.
- Ask before you add, remove, or upgrade any dependency.
- Before a change that touches more than one module, show a high-level design and wait for approval.
- Keep each body of work under 600 changed lines (added plus deleted). When it reaches 600, stop and report that the task scope or the design needs review.
- Run `mise run format`, `mise run check`, and `mise run build` without asking.

## Workflows

### Writing code

- Change only the code the task requires.
- Add error handling or validation only for cases that occur today.
- Add comments or docstrings only when the user explicitly requests them.
- Follow `docs/module-visibility-spec.md`. Apply these rules in design, because `mise run check` does not enforce them:
  - Put implementation and shared code in `src/stitch/core/_internal/`. Declare the published API outside `_internal`, in public modules and package `__init__.py` files that define members or re-export them from `_internal`. (A3, A4, V5)
  - Give a module whose members its package re-exports a private name, such as `_container.py`. Re-export through `__all__` or `from .module import Name as Name`. (V3, D1)
  - Import members exposed by a package from that package, not from its implementation modules. (I4)
  - Prefer many small modules to nested subpackages. Keep import paths to two segments. (L1, L3)
  - Make a member private when only its own module uses it. Remove unused public members. (V4)
  - Resolve an import cycle by changing dependencies or moving shared code. (I5)

### Large features and refactors

1. Add the new code as a new module or package.
2. Integrate its features into the existing code.
3. Ask before you replace the existing code that it supersedes.

### Committing

- Commit each small, complete step without asking.
- Write messages in the Conventional Commits format: `type(scope): summary`.
- State what changed, not why. Keep the wording short, clear, and declarative.
- Use a single-line message in most cases. When a body is necessary, limit it to five bullets.

### Writing tests

1. Confirm with the user which symbols to test.
2. Test only this package's own behavior. Cover each behavior once.

### Research

- Verify each detail against its definition or source before you rely on it, for example a mise task's `run` and `depends` entries or a function body.
- To learn how a library behaves, check its official documentation or Context7 first. If they do not answer the question, ask the user. Read library source in `.venv` as a last resort.

### Before you report a task as done

1. Run `mise run format`.
2. Run `mise run check` and fix every failure.
3. Review the changed code against the rules in `docs/module-visibility-spec.md` that `mise run check` does not enforce. Use a separate agent for this review if your harness supports one.

## Tooling

- mise: run project tasks with `mise run <task>`. Documentation: `https://mise.jdx.dev/llms.txt`.
- ast-grep (`ast-grep`): structural code search and rewrites. Project rules are in `.ast-grep/rules`, configured by `sgconfig.yml`. Documentation: `https://ast-grep.github.io/llms.txt`.
- sd (`sd`): find and replace text.
- Language server: when one is configured, use it to find definitions, references, and types. Use text search otherwise.
