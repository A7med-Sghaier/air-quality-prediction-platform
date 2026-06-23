# Security Notes

This repository is a sanitized portfolio copy of an older university project.

Do not commit:

- API tokens or competition submission tokens
- AWS credentials
- SSH private keys
- GitLab runner registration tokens
- MongoDB passwords or production connection strings
- Private server hostnames or deployment inventories

Use `.env.example` as the template for local configuration and keep real values in local environment variables or a private secret manager.
