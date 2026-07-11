# CI

`.github/workflows/_core.yml` (called by both `ci.yml` on push to `main` and
`pr.yml` on pull requests) runs three jobs: `mise run check`, `mise run test`,
and `mise run build` followed by a smoke test (`docker run` + curl
`/utils/health`).

`ci.yml` also calls `deploy.yml` with `needs: core`, so it only runs on push
to `main` and only after `core` passes. `pr.yml` does not call it, so PRs
never trigger a deploy attempt.

`deploy.yml` has two jobs, split by how the workflow was triggered:

- `deploy-dev` runs when called via `workflow_call` (i.e. automatically, from
  `ci.yml` after `core` passes) and targets the `dev` GitHub Environment.
- `deploy-prod` runs only on a manual `workflow_dispatch` ("Run workflow" in
  the Actions tab) and targets the `production` Environment.

Both jobs' `Deploy` steps are currently `echo` placeholders — the
trigger/gating and Environment wiring are real and don't need touching, only
the `run:` blocks need replacing with actual deploy commands once there's a
real target. Consider adding required reviewers on the `production`
Environment (repo Settings > Environments) to gate manual prod deploys.
