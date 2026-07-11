# CI

`.github/workflows/_core.yml` (called by both `ci.yml` on push to `main` and
`pr.yml` on pull requests) runs three jobs: `mise run check`, `mise run test`,
and `mise run build` followed by a smoke test (`docker run` + curl
`/utils/health`).

`ci.yml` also calls `deploy.yml` with `needs: core`, so it only runs on push
to `main` and only after `core` passes. `deploy.yml`'s job is currently a
no-op (`echo` placeholder) — the trigger/gating is real and doesn't need
touching, only the `Deploy` step's `run:` needs replacing with an actual
deploy once there's a real target. `pr.yml` does not call it, so PRs never
trigger a deploy attempt.
