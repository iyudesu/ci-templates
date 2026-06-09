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
│   ├── cmd/
│   ├── pkg/
│   ├── go.mod
│   ├── go.sum
│   └── Dockerfile
│
├── node-js/             # Node.js service
│   ├── src/
│   ├── package.json
│   ├── package-lock.json
│   └── Dockerfile
│
├── python/              # Python service
│   ├── app/
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
│   ├── go-ci.yml
│   ├── node-ci.yml
│   ├── python-ci.yml
│   ├── rust-ci.yml
│   ├── release.yml
│   ├── publish.yml
│   └── reusables/
│       ├── go.yml
│       ├── node.yml
│       ├── python.yml
│       ├── rust.yml
│       └── docker.yml
│
├── .releaserc.go.json
├── .releaserc.node-js.json
├── .releaserc.python.json
├── .releaserc.rust.json
│
├── package.json         # semantic-release dependencies
├── package-lock.json
│
├── README.md
└── .gitignore
```

---

# 🧠 Architecture Overview

## CI/CD Flow

```
git push (feature)
    ↓
Service-specific CI (lint + build + test)
    ↓
merge to main
    ↓
semantic-release (per service)
    ↓
Git tag created (e.g., node-v1.2.0)
    ↓
publish workflow triggered
    ↓
Docker image pushed to GHCR
```

---

# ⚙️ CI Workflows

Each service has its own CI pipeline:

| Service | Workflow        |
| ------- | --------------- |
| Go      | `go-ci.yml`     |
| Node.js | `node-ci.yml`   |
| Python  | `python-ci.yml` |
| Rust    | `rust-ci.yml`   |

### Features

* ✅ Path-based triggers (only run when service changes)
* ✅ Linting 
  - [golangci-lint](https://github.com/golangci/golangci-lint) (Go)
  - [eslint](https://github.com/eslint/eslint) (Node.js) to use ESlint, need Node.js version ^20.19.0, ^22.13.0, or >=24
  - [flake8](https://github.com/PyCQA/flake8) (Python)
  - [clippy](https://github.com/rust-lang/rust-clippy) (Rust)
* ✅ Build + Test
  - For Go, using built-in test 
  - [vitest](https://github.com/vitest-dev/vitest) (Node.js)
  - [pytest]() (Python)
  - For Rust, using built-in test 
* ✅ Dependency caching

---

# 🔁 Reusable Workflows

Located in:

```sh
.github/workflows/reusable/
```

Purpose:

* Avoid duplication
* Standardize CI logic
* Easy to scale

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

# 🚀 Release Workflow

File: `.github/workflows/release.yml`

* Runs on `main`
* Executes semantic-release per service
* Creates Git tags automatically

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

1. Create folder:

```
/new-service
```

2. Add:

* `Dockerfile`
* Build/test config

3. Create:

```
.releaserc.new-service.json
```

4. Add workflow:

```
.github/workflows/new-service-ci.yml
```

5. Update:

```
release.yml (matrix)
publish.yml (matrix)
```

---

# 👨‍💻 Local Development

Example:

### Go

```sh
cd go
go run ./cmd
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
