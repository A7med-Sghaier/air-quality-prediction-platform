# Deployment Notes

The original repository contained legacy Ansible deployment files for a university-hosted environment. Those files were removed from this portfolio-safe version because they included private infrastructure details and credentials.

For portfolio use, this repository keeps the local Docker Compose setup and CI build/test configuration. A modern deployment setup should be recreated with fresh secrets stored in the target platform's secret manager.
