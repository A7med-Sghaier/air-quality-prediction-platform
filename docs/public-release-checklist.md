# Public Release Checklist

This repository is currently intended to remain private until the original project ownership and safety checks are complete. Use this checklist before making the project public or pinning it as a portfolio repository.

## Ownership And Permission

- Confirm the project is a university/personal project and not owned by an employer, client, or private company.
- Confirm that publishing the code does not violate university, competition, team, or platform rules.
- Confirm that included datasets and trained model artifacts can be shared publicly.
- If ownership or licensing is unclear, keep the repository private or create a cleaned demo rewrite instead.

## Secret And Infrastructure Safety

- Rotate or revoke any credentials that existed in the original archive, even if they have now been removed.
- Confirm there are no AWS keys, SSH private keys, GitLab runner tokens, database passwords, API tokens, or competition tokens in the current repository.
- Confirm there are no private server hostnames, deployment inventories, or production connection strings.
- Keep real local configuration in environment variables or a private secret manager, not committed files.

Suggested local checks:

```bash
rg -n "AKIA|BEGIN RSA PRIVATE KEY|aws_secret_access_key|aws_access_key_id|team_token|root_password_hash|mongodb://.*:.*@|token\s*=|password" .
```

## Repository Hygiene

- Keep generated files, runtime database files, caches, and dependency folders out of Git.
- Keep large binary artifacts under Git LFS where they are intentionally part of the portfolio story.
- Confirm `.env.example` contains placeholders only.
- Confirm `SECURITY.md` explains what must not be committed.

## Build And Verification

- Confirm the GitHub Actions `Portfolio checks` workflow passes.
- Confirm Python syntax check passes locally:

```bash
python -m compileall -q server/air_pollution
```

- Verify the frontend with Docker or a matching legacy Node 8 environment.
- Document any verification limitations honestly in the README.

## Documentation Readiness

- README explains the project purpose, stack, local setup, verification, and portfolio value.
- Architecture documentation explains the Angular, Falcon API, MongoDB, preprocessing, and prediction flow.
- Public-release notes explain why the repository was sanitized.
- Screenshots or a short demo section should be added before pinning the project publicly.

## GitHub Profile Readiness

Recommended repository description:

```text
Full-stack air-quality prediction platform with Angular dashboard, Python Falcon API, MongoDB, Docker, and ML preprocessing workflows.
```

Recommended topics:

```text
angular typescript python falcon mongodb machine-learning data-visualization docker air-quality portfolio
```

## Final Decision

Recommended state before all checks are complete: private.

Recommended state after ownership, secret, data, and verification checks are complete: public portfolio repository, optionally pinned if screenshots/demo material are added.
