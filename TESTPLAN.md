# Test Plan — CI/CD Workflow Validation

## Trigger Reference

| Action | Jobs triggered |
|--------|----------------|
| Push to any branch with `go/**` changes | `go-ci.yml` → `lint` → `build` → `test` only |
| Push to `main` with `go/**` changes | `go-ci.yml` → `lint` → `build` → `test` → `release` → `publish` (if new tag) |
| Push to any branch with `node-js/**` changes | `node-ci.yml` → `lint` → `build` → `test` only |
| Push to `main` with `node-js/**` changes | `node-ci.yml` → `lint` → `build` → `test` → `release` → `publish` (if new tag) |
| Push to any branch with `python/**` changes | `python-ci.yml` → `lint` → `build` → `test` only |
| Push to `main` with `python/**` changes | `python-ci.yml` → `lint` → `build` → `test` → `release` → `publish` (if new tag) |
| Push to any branch with `rust/**` changes | `rust-ci.yml` → `lint` → `build` → `test` only |
| Push to `main` with `rust/**` changes | `rust-ci.yml` → `lint` → `build` → `test` → `release` → `publish` (if new tag) |
| Tag `*-v*` pushed manually | `publish.yml` → `reusable-publish.yml` (matching service only) |

---

## Step 1 — Validate YAML Syntax Locally

Install `actionlint` (validates GitHub Actions logic, not just YAML syntax):

```sh
# macOS
brew install actionlint
actionlint --version

# Run against all workflows
actionlint .github/workflows/*.yml
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

Monitor runs in the GitHub Actions UI:

1. Go to your repository on GitHub
2. Click the **Actions** tab
3. Filter by branch: use the branch dropdown and select `test/ci-validation`
4. Confirm 4 separate workflow runs appear — one per service

To view details of a run:

1. Click the workflow run name (e.g. **Go CI**)
2. You will see five jobs in sequence: **lint**, **build**, **test**, **Release** (skipped on feature branches), **Publish Docker Image** (skipped)
3. Click any job to expand its steps
4. A red ✗ means the job failed — click the step to expand the log

**Pass criteria:**
- 4 separate workflow runs appear, one per service
- Each run shows 5 jobs: lint, build, test, Release (skipped), Publish Docker Image (skipped)
- `lint` job may show as yellow ⚠ (warning) due to `continue-on-error: true` — this is expected
- `build` and `test` jobs must be green ✓ — these are blocking

---

## Step 3 — Test the Release and Publish Jobs

Release and publish are embedded in each service CI file and only run on `main`. Merge or push a scoped conventional commit to `main`:

```sh
git switch main && git pull

# Make a real change to a service file, then commit with a scoped message
git commit -m "fix(go): correct health check response message"
git push origin main
```

Monitor the run in the GitHub Actions UI:

1. Go to the **Actions** tab
2. Click **Go CI** in the left sidebar
3. Open the latest run — it shows five jobs: **lint**, **build**, **test**, **Release**, **Publish Docker Image**
4. Expand **Release** to see semantic-release output — a successful release prints `Published release X.X.X`
5. If a tag was created, **Publish Docker Image** runs next and pushes the image to GHCR
6. If no releasable commits exist, **Publish Docker Image** is skipped (grey)

Verify the tag was created:

```sh
git fetch --tags
git tag -l "go-v*"
```

Or on GitHub: go to **Code** → **Tags** and confirm a `go-v*` tag appears.

**Pass criteria:**
- `Go CI` run shows all five jobs: lint ✓, build ✓, test ✓, Release ✓, Publish Docker Image ✓ (or skipped if no releasable commit)
- A `go-v*` tag appears under **Code → Tags** when a releasable commit was pushed
- Only the Go service pipeline triggers — Node, Python, Rust are not affected

---

## Step 4 — Test the Publish Workflow

If Step 3 succeeded, the `go-v*` tag push auto-triggers `publish.yml`. To verify:

1. Go to the **Actions** tab
2. Click **Publish Images** in the left sidebar
3. Open the latest run triggered by the `go-v*` tag

To trigger manually without going through semantic-release:

```sh
git tag go-v0.0.1-test
git push origin go-v0.0.1-test
```

Inspect the run:

1. Open the **Publish Images** run in the **Actions** tab
2. Confirm only the **go** job ran — `node`, `python`, and `rust` jobs should show as **skipped** (grey, not green or red)
3. Inside the `docker` job, expand **Build & Push** to confirm the image was pushed to GHCR

Verify the image exists:

1. Go to your GitHub profile → **Packages**
2. Confirm a new package named after the service appears with the pushed tag

**Pass criteria:**
- Only the `go` job runs — all other jobs show as skipped
- The Docker image appears under **Packages** with the correct tag

---

## Step 5 — Verify PR Trigger Behavior

The CI workflows currently exclude PRs targeting `main`:

```yaml
pull_request:
  branches: ['**', '!main']
```

This means opening a PR to `main` does **not** trigger CI — only the post-merge push does.

To test this behavior:

1. Open a PR from `test/ci-validation` → `main` on GitHub
2. Go to the **Actions** tab and confirm no new CI run appears for the PR
3. The PR status checks section should show no pending checks

If pre-merge CI on `main` PRs is required, update each `*-ci.yml`:

```yaml
pull_request:
  branches: ['**']   # remove the '!main' exclusion
```

---

## Cleanup

Remove test branches and tags:

```sh
git push origin --delete test/ci-validation
git tag -d go-v0.0.1-test
git push origin --delete go-v0.0.1-test
```

On GitHub, confirm the branch and tag are gone under **Code → Branches** and **Code → Tags**.
