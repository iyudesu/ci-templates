# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Repo Is

A polyglot monorepo with four independent HTTP microservices (Go, Node.js, Python, Rust), each with its own CI pipeline, Dockerfile, and semantic versioning. The root `package.json` only holds `semantic-release` tooling — it is not a service.

## Local Development Commands

### Go (`go/`)
```sh
cd go
go run .           # run
go build ./...     # build
go test ./...      # test
```
Uses `golangci-lint` for linting (run via the GitHub Action; no local config file present).

### Node.js (`node-js/`)
```sh
cd node-js
npm ci             # install deps
npm run build      # babel transpile src/ → dist/
npm start          # run (requires build first)
npx eslint .       # lint
npx vitest run     # test
```
Requires Node.js `^20.19.0`, `^22.13.0`, or `>=24` for ESLint.

### Python (`python/`)
```sh
cd python
pip install -r requirements.txt
python3 app.py     # run (Flask on :8080)
flake8             # lint
pytest             # test (files must match test_*.py or *_test.py)
```

### Rust (`rust/`)
```sh
cd rust
cargo run          # run
cargo build --release
cargo clippy -- -D warnings   # lint
cargo clippy --fix --allow-dirty  # auto-fix (applies to whole workspace, not single files)
cargo test
```

## Architecture

### Service Pattern
All four services are identical in behavior: Express/Flask/Actix/net-http servers on port 8080 with three routes:
- `GET /` — greeting
- `GET /health/readiness` — returns 200 if `/tmp/ready` exists, else 503
- `GET /health/liveness` — same check

The liveness/readiness probe pattern relies on `/tmp/ready` existing at runtime (e.g., created by an init container or startup script in Kubernetes).

### CI/CD Flow
Each service CI file (`go-ci.yml` etc.) runs five sequential jobs:

```
push to any branch (service files or its workflow files changed)
    → [job: lint]    reusable-<service>-lint.yml   — warn-only (continue-on-error)
    → [job: build]   reusable-<service>-build.yml  — blocking
    → [job: test]    reusable-<service>-test.yml   — blocking
    → [job: release] reusable-release.yml           — main only, semantic-release → tag
    → [job: publish] reusable-publish.yml           — only if new tag, push to GHCR
```

`release` and `publish` are skipped on feature branches. `publish.yml` still exists for manual re-publishing via a direct tag push.

### Reusable Workflows
All at the top level of `.github/workflows/` (GitHub Actions requires local `./` workflow references to be at the top level). Each CI stage has its own dedicated reusable file:

- **Per-language**: `reusable-<service>-lint.yml`, `reusable-<service>-build.yml`, `reusable-<service>-test.yml`
- **Shared**: `reusable-release.yml` (inputs: `service`, `releaserc`, `tag_pattern`; output: `new_tag`), `reusable-publish.yml` (inputs: `service`, `version`)

### Docker Images
Published to `ghcr.io/<owner>/<repo>/<service>:<tag>` on per-service tag push (`go-v*`, `node-v*`, etc.). Authentication uses the built-in `GITHUB_TOKEN` — no manual secret setup needed. Required workflow permissions: `contents: read`, `packages: write`.

## Commit Convention

Commits must use **scoped conventional commits** for semantic-release to version services independently:

```
feat(node): add authentication     → minor bump for node
fix(go): handle nil pointer        → patch bump for go
feat(python)!: breaking change     → major bump for python
```

The scope (`go`, `node`, `python`, `rust`) determines which service gets a new version tag (e.g., `node-v2.3.1`).

## Adding a New Service

1. Create `/<service>/` with a `Dockerfile` and build/test config
2. Add `reusable-<service>-lint.yml`, `reusable-<service>-build.yml`, `reusable-<service>-test.yml`
3. Add `.github/workflows/<service>-ci.yml` calling all five reusable stages; pass `service`, `releaserc`, and `tag_pattern` to `reusable-release.yml`
4. Create `.releaserc.<service>.json` with scoped `releaseRules` and `tagFormat: "<service>-v${version}"`
5. Add a new job with `if: startsWith(github.ref, 'refs/tags/<service>-v')` in `publish.yml`
