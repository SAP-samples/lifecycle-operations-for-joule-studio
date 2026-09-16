# lifecycle-operations-for-joule-studio

This repository contains the reference pipeline configurations and setup guides for promoting Joule Studio solutions from a Development tenant to a Production tenant via a git provider.

Joule Studio uses a CI/CD pipeline as the deliberate promotion gate between environments. When a solution is pushed to a connected git repository, the pipeline files are included automatically. The pipeline can then be manually triggered to create and deploy the solution in the Production tenant. This repository provides the reference pipeline files and step-by-step setup instructions for each supported git provider.

## End-to-end promotion flow

### One-time setup

**Step 1 — Configure trust between SAP Cloud Identity Services and the git provider**

Before any solution can be promoted, the provider-specific setup documented in this repository must be completed. The setup guides each cover two steps:

- **Create an application in SAP Cloud Identity Services** (Production tenant). This produces the client credentials that the pipeline will use to authenticate against the Production environment.
- **Store those credentials as secured CI/CD variables** in the git provider (`SCI_TENANT_URL`, `SCI_CLIENT_ID`, `SCI_CLIENT_SECRET`, `JOULE_STUDIO_URL`, and any provider-specific variables) so the pipeline can read them at runtime without exposing secrets in code.

See the [setup guides](#setup-guides) below for the detailed instructions for your git provider.

**Step 2 — Register the git provider in Joule Studio Admin Settings**

Register the git provider connection in **Joule Studio Admin Settings**. This makes the provider available when connecting a solution to a repository.

### Per-solution setup

**Step 3 — Connect the solution to a repository**

From the Development tenant, open the solution in Joule Studio and connect it to a repository hosted on one of the configured git providers.

**Step 4 — Push the solution**

Push the solution to the git provider. Joule Studio automatically includes the pipeline or workflow file in the push — no manual file creation is needed. After the push, the repository contains both the solution content and the CI/CD definition required for promotion.

### Promotion

**Step 5 — Trigger the pipeline to promote to Production**

Trigger the pipeline or workflow manually. The pipeline performs two sequential operations against the Production tenant:

1. **Create the solution** — registers the solution in the Production tenant.
2. **Deploy the solution** — triggers the deployment in the Production tenant.

The pipeline authenticates using the credentials configured in Step 1 and calls the Joule Studio solution management API on the Production tenant.

---

## Supported git providers

| Provider | Folder | Pipeline file |
|---|---|---|
| GitHub | [github/](github/) | `.github/workflows/deploy.yml` |
| GitLab | [gitlab/](gitlab/) | `deploy.yml` |
| Azure DevOps | [azure/](azure/) | `deploy.yml` |
| Bitbucket | [bitbucket/](bitbucket/) | `bitbucket-pipelines.yml` |

## Setup guides

Each provider folder contains a `SETUP.md` with end-to-end instructions covering Step 1 (SCI configuration and CI/CD variable setup):

- [GitHub Setup](github/SETUP.md)
- [GitLab Setup](gitlab/SETUP.md)
- [Azure DevOps Setup](azure/SETUP.md)
- [Bitbucket Setup](bitbucket/SETUP.md)

## Authentication model

The pipeline authenticates to the Production tenant's SCI using OAuth 2.0 client credentials. All supported providers store the client ID and client secret as secured CI/CD variables and exchange them for an SCI access token at pipeline runtime. No secrets are embedded in the pipeline files committed to the repository.

## Related resources

- [Joule Studio Deployment Guide](https://help.sap.com/docs/business-ai-platform/joule-studio/deployment)
- [Joule Studio Provisioning](https://help.sap.com/docs/business-ai-platform/joule-studio/provisioning)
- [SAP Cloud Identity Services Documentation](https://help.sap.com/docs/identity-authentication)
