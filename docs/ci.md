# CI

`.github/workflows/_core.yml` (called by both `ci.yml` on push to `main` and
`pr.yml` on pull requests) runs three jobs: `mise run check`, `mise run test`,
and `mise run build` followed by a smoke test (`docker run` + curl
`/utils/health`). `deploy.yml` is an intentionally unwired placeholder — see
its comments for the pattern to fill in once there's a real deploy target.
