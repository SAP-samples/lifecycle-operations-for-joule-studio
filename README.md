# lifecycle-operations-for-joule-studio

This repository contains the reference pipeline configurations and setup guides for promoting Joule Studio solutions to production via a git provider.

When a developer is ready to deploy a solution to a productive environment, Joule Studio uses a CI/CD pipeline as the deliberate approval gate. The developer pushes their solution to a connected git repository, and an administrator manually triggers the pipeline to perform the deployment. This repository provides the reference files that Joule Studio pushes into each connected repository, along with step-by-step setup instructions for each supported git provider.

## Supported Git Providers

| Provider | Folder | Pipeline file |
|---|---|---|
| GitHub | [github/](github/) | `.github/workflows/deploy.yml` |
| GitLab | [gitlab/](gitlab/) | `deploy.yml` |
| Azure DevOps | [azure/](azure/) | `deploy.yml` |
| Bitbucket | [bitbucket/](bitbucket/) | `bitbucket-pipelines.yml` |

## Setup

Each provider folder contains a `SETUP.md` with end-to-end instructions:

- [GitHub Setup](github/SETUP.md)
- [GitLab Setup](gitlab/SETUP.md)
- [Azure DevOps Setup](azure/SETUP.md)
- [Bitbucket Setup](bitbucket/SETUP.md)

All providers follow the same high-level flow:

1. Establish trust between SAP Cloud Identity Services (SCI) and the git provider using OIDC or client credentials.
2. Configure the required CI/CD variables (`SCI_TENANT_URL`, `SCI_CLIENT_ID`, `JOULE_STUDIO_URL`, and provider-specific variables).
3. Connect your Joule Studio solution to the repository and push — the pipeline files are included automatically.
4. Manually trigger the pipeline to deploy the solution to the productive environment.

## Authentication model

Each provider uses a keyless or low-secret authentication approach where possible:

- **GitHub** and **GitLab** use OAuth 2.0 client credentials — a client ID and client secret are stored as secured repository variables and exchanged for an SCI access token.
- **Azure DevOps** uses OAuth 2.0 client credentials — a client ID and client secret are stored as secured repository variables and exchanged for an SCI access token.
- **Bitbucket** uses OAuth 2.0 client credentials — a client ID and client secret are stored as secured repository variables and exchanged for an SCI access token.

## Related resources

- [Joule Studio Deployment Guide](https://help.sap.com/docs/business-ai-platform/joule-studio/deployment)
- [Joule Studio Provisioning](https://help.sap.com/docs/business-ai-platform/joule-studio/provisioning)
- [SAP Cloud Identity Services Documentation](https://help.sap.com/docs/identity-authentication)
