# Test Plan — CI/CD Workflow Validation (Gitflow)

## Gitflow Branching Model

```
main          ← stable production releases only
  ↑ merge via PR
release/*     ← release preparation (RC testing)
  ↑ branch from / merge into
develop       ← integration branch, next release
  ↑ merge via PR
feature/*     ← new features
hotfix/*      ← urgent production fixes (branch from main, merge into main + develop)
```

### Branch CI Behaviour

| Event | CI stages triggered | Release & Publish |
|-------|--------------------|--------------------|
| Push to `feature/**` | lint → build → test | No |
| Push to `develop` | lint → build → test | No |
| Push to `release/**` | lint → build → test | No |
| Push to `hotfix/**` | lint → build → test | No |
| PR opened/updated → `develop` or `release/**` | lint → build → test | No |
| PR opened/updated → `main` | lint → build → test | No |
| Push to `main` (i.e. a merged PR) | lint → build → test → release → publish | Yes (on new tag) |

> **Note:** Release runs on the `push` to `main`, not on the PR-merge event. semantic-release refuses to run inside a `pull_request` event (`env-ci` flags it as a PR), so it must be driven by the push that a merge produces. Block direct pushes to `main` with GitHub **branch protection** (Settings → Branches → require a PR before merging).

---

## Trigger Reference

| Action | Jobs triggered |
|--------|----------------|
| Push to `feature/**` with `go/**` changes | `go-ci.yml` → lint → build → test |
| Push to `develop` with `go/**` changes | `go-ci.yml` → lint → build → test |
| PR opened/updated from `feature/*` → `develop` | lint → build → test per changed service |
| PR opened/updated from `release/*` → `main` | lint → build → test per changed service |
| Push to `main` (a merged PR) with `go/**` changes | lint → build → test → release → publish (if new tag) |
| Tag `*-v*` pushed manually | `publish.yml` → `reusable-publish.yml` (matching service only) |

Same pattern applies for `node-js/**`, `python/**`, `rust/**`.

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

## Step 2 — Test Feature Branch CI (lint + build + test)

Simulate a developer working on a feature branch:

```sh
# Start from develop (create it locally if it doesn't exist)
git switch -c develop 2>/dev/null || git switch develop

# Push develop to remote so it can be the PR base in Step 3.
# Without a remote develop branch, GitHub has nothing to compare against.
git push origin develop

# Create a feature branch
git switch -c feature/ci-test

# Make a small change per service to trigger CI
touch go/.ci-test        && git add go/.ci-test        && git commit -m "test(go): trigger CI"
touch node-js/.ci-test   && git add node-js/.ci-test   && git commit -m "test(node): trigger CI"
touch python/.ci-test    && git add python/.ci-test    && git commit -m "test(python): trigger CI"
touch rust/.ci-test      && git add rust/.ci-test      && git commit -m "test(rust): trigger CI"

git push origin feature/ci-test
```

Monitor runs in the GitHub Actions UI:

1. Go to your repository on GitHub
2. Click the **Actions** tab
3. Use the branch dropdown and select `feature/ci-test`
4. Confirm 4 separate workflow runs appear — one per service

To view details of a run:

1. Click the workflow run name (e.g. **Go CI**)
2. You will see five jobs: **lint**, **build**, **test**, **Release** (skipped), **Publish Docker Image** (skipped)
3. Click any job to expand its steps
4. A red ✗ means the job failed — click the step to expand the log

**Pass criteria:**
- 4 separate workflow runs appear, one per service
- Each run shows 5 jobs: lint ✓/⚠, build ✓, test ✓, Release ⊘ (skipped), Publish ⊘ (skipped)
- `lint` may show yellow ⚠ due to `continue-on-error: true` — expected
- `build` and `test` must be green ✓

---

## Step 3 — Test PR Trigger (feature → develop)

Open a pull request from `feature/ci-test` → `develop`.

> **Prerequisite:** `develop` must exist on the remote (pushed in Step 2). GitHub can only compare two branches that both exist on the remote — without a remote `develop`, the base dropdown has nothing to select.

1. On GitHub, go to **Pull requests** → **New pull request**
2. Set base: `develop`, compare: `feature/ci-test`
3. Submit the PR

In the **Actions** tab, confirm CI runs again — the `pull_request` trigger fires for PRs targeting `develop`.

**Pass criteria:** Same 4 workflow runs appear, `release` and `publish` skipped.

---

## Step 4 — Test merge to main (Release and Publish)

The full pipeline (including release + publish) fires on a **push to `main`**. Merging a PR into `main` produces that push, so this is the normal release path. Use a scoped conventional commit so semantic-release creates a tag:

```sh
git switch develop && git pull

# Make a real change to a service file
echo "# test" >> go/README.md
git add go/README.md
git commit -m "fix(go): correct health check response message"
git push origin develop

# Open a PR from develop → main on GitHub, then merge it
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

## Step 5 — Test Hotfix Flow

Hotfixes branch from `main` and merge back into both `main` and `develop`:

```sh
git switch main && git pull
git switch -c hotfix/fix-critical-bug

# Make the fix with a scoped commit
git commit -m "fix(go): patch critical nil pointer"
git push origin hotfix/fix-critical-bug
```

1. Open PR: `hotfix/fix-critical-bug` → `main`
2. CI runs lint + build + test (pass criteria same as Step 2)
3. After merging to `main`, release + publish fire automatically (same as Step 4)
4. Also open PR: `hotfix/fix-critical-bug` → `develop` to keep it in sync

**Pass criteria:** CI passes on the hotfix branch; after merge to `main`, release is created.

---

## Step 6 — Test the Publish Workflow (Manual Tag)

To trigger `publish.yml` directly without going through semantic-release:

```sh
git tag go-v0.0.1-test
git push origin go-v0.0.1-test
```

Inspect the run:

1. Open the **Publish Images** run in the **Actions** tab
2. Confirm only the **go** job ran — `node`, `python`, and `rust` jobs show as **skipped** (grey)
3. Inside the `docker` job, expand **Build & Push** to confirm the image was pushed to GHCR

Verify the image exists:

1. Go to your GitHub profile → **Packages**
2. Confirm a new package named after the service appears with the pushed tag

**Pass criteria:**
- Only the `go` job runs — all other jobs show as skipped
- The Docker image appears under **Packages** with the correct tag

---

## Cleanup

Remove test branches and tags after validation:

```sh
git push origin --delete feature/ci-test
git push origin --delete hotfix/fix-critical-bug
git tag -d go-v0.0.1-test
git push origin --delete go-v0.0.1-test
```

On GitHub, confirm the branches and tags are gone under **Code → Branches** and **Code → Tags**.
