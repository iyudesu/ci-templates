# Test Plan — CI/CD Workflow Validation

## Trigger Reference

| Action | Workflow triggered |
|--------|-------------------|
| Push to any branch with `go/**` changes | `go-ci.yml` → `reusables/go.yml` |
| Push to any branch with `node-js/**` changes | `node-ci.yml` → `reusables/node.yml` |
| Push to any branch with `python/**` changes | `python-ci.yml` → `reusables/python.yml` |
| Push to any branch with `rust/**` changes | `rust-ci.yml` → `reusables/rust.yml` |
| Push to `main` | `release.yml` (semantic-release per service) |
| Tag `go-v*` pushed | `publish.yml` → `reusables/docker.yml` (go job only) |
| Tag `node-v*` pushed | `publish.yml` → `reusables/docker.yml` (node job only) |
| Tag `python-v*` pushed | `publish.yml` → `reusables/docker.yml` (python job only) |
| Tag `rust-v*` pushed | `publish.yml` → `reusables/docker.yml` (rust job only) |

---

## Step 1 — Validate YAML Syntax Locally

Install `actionlint` (validates GitHub Actions logic, not just YAML syntax):

```sh
# macOS
brew install actionlint
actionlint --version

# Run against all workflows
actionlint .github/workflows/*.yml .github/workflows/reusables/*.yml
```

Basic YAML lint:

```sh
pip3 install yamllint
yamllint --version
yamllint .github/workflows/
```

**Pass criteria:** No errors from either tool.

---

## Step 2 — Test CI Workflows (lint + build + test)

Create a test branch and push a small change per service to trigger each CI pipeline independently.

```sh
git switch -c test/ci-validation

# Trigger Go CI
touch go/.ci-test && git add go/.ci-test && git commit -m "test(go): trigger CI"

# Trigger Node CI
touch node-js/.ci-test && git add node-js/.ci-test && git commit -m "test(node): trigger CI"

# Trigger Python CI
touch python/.ci-test && git add python/.ci-test && git commit -m "test(python): trigger CI"

# Trigger Rust CI
touch rust/.ci-test && git add rust/.ci-test && git commit -m "test(rust): trigger CI"

git push origin test/ci-validation
```

Monitor runs:

```sh
gh run list --branch test/ci-validation
gh run watch        # streams the latest run live
```

View logs for a failed run:

```sh
gh run view <run-id> --log-failed
```

**Pass criteria:**
- 4 separate workflow runs appear, one per service
- Each run calls its reusable workflow (visible as a nested job)
- Lint, build, and test steps all pass without `|| true` masking

---

## Step 3 — Test the Release Workflow

The release workflow triggers on every push to `main`. Use a scoped conventional commit so semantic-release detects a version bump for the target service.

```sh
git switch main && git pull

# Make a real change to a service file, then commit with a scoped message
git commit -m "fix(go): correct health check response message"
git push origin main
```

Monitor the release run:

```sh
gh run list --workflow=release.yml
gh run watch
```

Verify the tag was created:

```sh
git fetch --tags
git tag -l "go-v*"
```

**Pass criteria:**
- `release.yml` runs a matrix of 4 jobs (one per service)
- Only the `go` job creates a new tag (others find no releasable commits)
- A `go-v*` tag appears in the repository

---

## Step 4 — Test the Publish Workflow

If Step 3 succeeded, the `go-v*` tag push should have auto-triggered `publish.yml`. Verify:

```sh
gh run list --workflow=publish.yml
```

To trigger manually without going through semantic-release:

```sh
git tag go-v0.0.1-test
git push origin go-v0.0.1-test
```

**Pass criteria:**
- Only the `go` job runs — the `node`, `python`, and `rust` jobs are skipped by their `if:` guards
- The Docker image is pushed to GHCR

Verify the image exists in GHCR:

```sh
gh api /user/packages?package_type=container | jq '.[].name'
```

---

## Step 5 — Verify PR Trigger Behavior

The CI workflows currently exclude PRs targeting `main`:

```yaml
pull_request:
  branches: ['**', '!main']
```

This means opening a PR to `main` does **not** trigger CI — only the post-merge push does.

To test this behavior: open a PR from `test/ci-validation` → `main` and confirm no CI run is triggered for the PR itself.

If pre-merge CI on `main` PRs is required, update each `*-ci.yml`:

```yaml
pull_request:
  branches: ['**']   # remove the '!main' exclusion
```

---

## Cleanup

Remove test commits and tags after validation:

```sh
git push origin --delete test/ci-validation
git tag -d go-v0.0.1-test
git push origin --delete go-v0.0.1-test
```
