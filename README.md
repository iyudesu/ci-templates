# 🚀 Polyglot Monorepo CI/CD (Go · Node.js · Python · Rust)

This repository is a **polyglot monorepo** designed for scalable microservices development with:

* ⚡ Optimized GitHub Actions (per-service CI)
* 🔁 Reusable workflows (`workflow_call`)
* 🧠 True **per-service semantic versioning**
* 🐳 Dockerized services
* 📦 Automatic publishing to GitHub Container Registry (GHCR)

---

# 📁 Repository Structure

```sh
repo-root/
│
├── go/                  # Go service
│   ├── main.go
│   ├── go.mod
│   └── Dockerfile
│
├── node-js/             # Node.js service
│   ├── src/             # app.js, app.test.js
│   ├── package.json
│   ├── package-lock.json
│   └── Dockerfile
│
├── python/              # Python service
│   ├── app.py
│   ├── test_app.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── rust/                # Rust service
│   ├── src/
│   ├── Cargo.toml
│   ├── Cargo.lock
│   └── Dockerfile
│
├── .github/workflows/
│   ├── go-ci.yml            # full pipeline: lint → build → test → release → publish
│   ├── node-ci.yml
│   ├── python-ci.yml
│   ├── rust-ci.yml
│   ├── publish.yml          # manual re-publish via tag push
│   ├── reusable-go-lint.yml
│   ├── reusable-go-build.yml
│   ├── reusable-go-test.yml
│   ├── reusable-node-lint.yml
│   ├── reusable-node-build.yml
│   ├── reusable-node-test.yml
│   ├── reusable-python-lint.yml
│   ├── reusable-python-build.yml
│   ├── reusable-python-test.yml
│   ├── reusable-rust-lint.yml
│   ├── reusable-rust-build.yml
│   ├── reusable-rust-test.yml
│   ├── reusable-release.yml  # shared: semantic-release (parameterised by service)
│   └── reusable-publish.yml  # shared: docker build & push
│
├── .releaserc.go.json
├── .releaserc.node-js.json
├── .releaserc.python.json
├── .releaserc.rust.json
│
├── .yamllint.yml        # yamllint rule overrides for GitHub Actions
├── package.json         # semantic-release dependencies
├── package-lock.json
│
├── README.md
└── .gitignore
```

---

# 🧠 Architecture Overview

## CI/CD Flow

Each service CI file runs the **full pipeline** as five sequential jobs:

```
push to any branch (service or workflow files changed)
    ↓
[job: lint]   lint (warn-only, continue-on-error)
    ↓
[job: build]  compile / transpile / install deps
    ↓
[job: test]   run test suite
    ↓ (main branch only)
[job: release]  semantic-release → creates tag (e.g. go-v1.2.0)
    ↓ (only if new tag was created)
[job: publish]  docker build & push to GHCR
```

On feature branches only `lint`, `build`, and `test` run. `release` and `publish` are skipped.

---

# ⚙️ CI Workflows

Each service has its own self-contained pipeline:

| Service | Workflow | Jobs |
| ------- | -------- | ---- |
| Go      | `go-ci.yml`     | lint → build → test → release → publish |
| Node.js | `node-ci.yml`   | lint → build → test → release → publish |
| Python  | `python-ci.yml` | lint → build → test → release → publish |
| Rust    | `rust-ci.yml`   | lint → build → test → release → publish |

### Features

* ✅ Path-based triggers — fires on service files or its own workflow files
* ✅ Lint (warn-only, `continue-on-error: true`)
  - [golangci-lint](https://github.com/golangci/golangci-lint) (Go)
  - [eslint](https://github.com/eslint/eslint) (Node.js, requires `^20.19.0`, `^22.x`, or `>=24`)
  - [flake8](https://github.com/PyCQA/flake8) (Python)
  - [clippy](https://github.com/rust-lang/rust-clippy) (Rust)
* ✅ Build + Test (blocking)
  - Go: `go build`, `go test`
  - Node.js: `npm run build` (Babel), [vitest](https://github.com/vitest-dev/vitest)
  - Python: [pytest](https://docs.pytest.org)
  - Rust: `cargo build`, `cargo test`
* ✅ Release — semantic-release on `main` push, skipped on feature branches
* ✅ Publish — Docker image to GHCR, only when a new tag is created
* ✅ Dependency caching

---

# 🔁 Reusable Workflows

Each CI stage has its own dedicated reusable workflow file, located at the top level of `.github/workflows/` with a `reusable-` prefix:

| Stage | Files |
| ----- | ----- |
| Lint  | `reusable-go-lint.yml`, `reusable-node-lint.yml`, `reusable-python-lint.yml`, `reusable-rust-lint.yml` |
| Build | `reusable-go-build.yml`, `reusable-node-build.yml`, `reusable-python-build.yml`, `reusable-rust-build.yml` |
| Test  | `reusable-go-test.yml`, `reusable-node-test.yml`, `reusable-python-test.yml`, `reusable-rust-test.yml` |
| Release | `reusable-release.yml` (shared — accepts `service`, `releaserc`, `tag_pattern` inputs) |
| Publish | `reusable-publish.yml` (shared — accepts `service`, `version` inputs) |

> **Why top-level?** GitHub Actions only supports local `./` reusable workflow references at the top level of `.github/workflows/`. Subdirectories are not supported for local paths — they require the full `owner/repo/...@ref` format instead.

Benefits of per-stage reusable workflows:

* Each stage can be inspected, re-run, or replaced independently
* Release and publish logic is shared across all four services via `reusable-release.yml` and `reusable-publish.yml`
* Clear separation of concerns in the Actions UI (five distinct jobs per run)

---

# 🔍 YAML Linting

Workflow files are validated locally with [yamllint](https://github.com/adrienverge/yamllint).

```sh
pip3 install yamllint
yamllint .github/workflows/
```

### Configuration — `.yamllint.yml`

GitHub Actions YAML has conventions that conflict with yamllint's defaults. The `.yamllint.yml` file at the repo root overrides three rules:

| Rule | Setting | Reason |
| ---- | ------- | ------ |
| `truthy` | `check-keys: false` | GitHub Actions requires the bare `on:` trigger key. YAML 1.1 parses it as boolean `true`, which yamllint flags. Quoting it as `"on":` breaks nothing but deviates from universal Actions convention — so key checking is disabled instead. |
| `document-start` | `disable` | `---` document start is optional in YAML and is not used in GitHub Actions files by convention. |
| `line-length` | `max: 120` | GitHub Actions expressions (`${{ secrets.TOKEN }}`) and Docker commands naturally exceed the 80-char default. 120 is a reasonable limit for CI YAML. |

---

# 🧪 Semantic Versioning (Per Service)

Each service is versioned independently using **semantic-release**.

## Tag Format

```
go-v1.0.0
node-v2.3.1
python-v0.5.0
rust-v3.0.0
```

---

## Commit Convention (Required)

Use **scoped conventional commits**:

```sh
feat(node): add authentication
fix(go): handle nil pointer
feat(python): add worker
```

### Version Rules

| Commit Type | Version |
| ----------- | ------- |
| `fix:`      | Patch   |
| `feat:`     | Minor   |
| `feat!:`    | Major   |

---

# 🐳 Docker Publishing

Triggered by per-service Git tags:

```
go-v*
node-v*
python-v*
rust-v*
```

## Image Naming

```
ghcr.io/<owner>/<repo>/<service>:<version>
```

### Example

```
ghcr.io/your-org/monorepo/node:1.2.0
```

---

# 🔐 GitHub Container Registry (GHCR)

No manual setup required.

### Authentication

Uses built-in:

```
GITHUB_TOKEN
```

### Required Permissions

```yaml
permissions:
  contents: read
  packages: write
```

---

# ⚡ Performance Optimizations

* 🔹 Path-based CI triggers
* 🔹 Parallel workflows per service
* 🔹 Dependency caching
* 🔹 Docker layer optimization
* 🔹 Reusable workflows

---

# 🧩 Adding a New Service

1. Create `/<service>/` with source code, `Dockerfile`, and build/test config
2. Add a test file (`test_*.py`, `*.test.js`, etc.)
3. Add `reusable-<service>-lint.yml`, `reusable-<service>-build.yml`, `reusable-<service>-test.yml`
4. Add `.github/workflows/<service>-ci.yml` — call the three stage reusables, then call `reusable-release.yml` and `reusable-publish.yml` with the service-specific inputs
5. Create `.releaserc.<service>.json` with scoped release rules and `tagFormat: "<service>-v${version}"`
6. Add a new job with `if: startsWith(github.ref, 'refs/tags/<service>-v')` in `publish.yml`

---

# 👨‍💻 Local Development

Example:

### Go

```sh
cd go
# Run
go run .
# Build
go build ./...
# Lint (requires golangci-lint: https://golangci-lint.run/welcome/install/)
golangci-lint run
# Test
go test ./...
```

### Node.js

```sh
cd node-js
# Install
npm ci
# Run (build first)
npm run build
npm start
# Lint & fix
npx eslint .
npx eslint . --fix
# Test
npx vitest run
```

### Python

```sh
cd python
# Run
pip3 install -r requirements.txt
python3 app.py
# Lint with tool
pip3 install flake8
flake8
# Test (should create test_*.py or *_test.py to use this command to test)
pytest
```

### Rust

```sh
cd rust
# Run
cargo run
# Lint
cargo check
# Lint with tool
cargo clippy
# Fix, Warning! It can't be target for specific file or directory. Use command cargo clippy --fix to see unconcern changes and avoid them
cargo clippy --fix --allow-dirty
# Test
cargo test
```

---

# 📌 Summary

This monorepo provides:

* 🧩 Independent service lifecycle
* 🚀 Fast CI/CD pipelines
* 🐳 Container-first deployment
* 🔁 Scalable architecture

---

# 📄 License

MIT
