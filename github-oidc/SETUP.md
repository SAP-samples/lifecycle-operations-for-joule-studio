# GitHub Setup for Joule Studio

## Overview

Production deployment in Joule Studio uses GitHub Actions as the promotion mechanism. A developer pushes their solution to a GitHub repository, and an administrator manually triggers the deployment workflow to deploy it to the productive environment. This manual trigger is the deliberate approval gate for production.

> **Note:** GitHub setup is only required once you are ready to promote a solution to production. It is not a prerequisite for building, testing, or running solutions in the development environment. Development deployments can be performed directly from Joule Studio. See [Deployment](https://help.sap.com/docs/business-ai-platform/joule-studio/deployment).

---

## Prerequisites

- Core Components, Joule, and Joule Studio are provisioned for both environments.
- Your organization has a GitHub account, and GitHub Actions is enabled for the repository. The GitHub instance must be internet-accessible.
- You have administrator access to your SAP Cloud Identity Services (SCI) tenant.
- You are a GitHub organization owner, or an organization owner can configure Actions secrets and repository access for you.
- You have repository administrator access to configure the repository's OIDC subject template.

---

## Step 1: Create an Application in SAP Cloud Identity Services

Authentication between GitHub Actions and Joule Studio uses GitHub's OpenID Connect support. The workflow exchanges a short-lived GitHub-issued JWT for a Cloud Identity Services access token, which it then uses to call the Joule Studio solution management API.

### Create the Application

1. Log in to the SCI administration console at `https://<your-sci-tenant>.accounts.ondemand.com/admin`.

2. Go to **Applications & Resources** and select the **Applications** tile.

3. Select **Create** and fill in the dialog:
   - **Display Name:** Use a name that identifies your GitHub organization or repository, for example `github.com/<your-org>`.
   - **Type:** Non-SAP solution
   - **Parent application:** None
   - **Organization ID:** global
   - **Protocol Type:** OpenID Connect

4. Select **Create** and open the newly created application.

### Obtain the Client ID

1. On the **Trust** tab, under **Application APIs**, select **Client Authentication**.

2. The **Client ID** is displayed here. Note this value — you will need it as the `SCI_CLIENT_ID` organization secret in Step 2.


### Define a Dependency to the Joule Studio Application

1. Still on the **Trust** tab, under **Application APIs**, select **Dependencies**.

2. Select **Add** and fill in the dialog:
   - **Dependency Name:** `build`
   - **Application:** Search `Joule Studio` and find your Joule Studio application in the list.
   - **API:** Select `solution-deployment`

3. Select **Save**.

---

## Step 2: Configure Organization Secrets in GitHub

Set the following values at the **organization level**, under **Settings > Secrets and variables > Actions > Secrets**. Select **New organization secret** for each value. Use **Secrets**, not **Variables**.

| Secret | Description |
|---|---|
| `SCI_TENANT_URL` | Issuer URI of your SAP Cloud Identity Services tenant, e.g. `https://<your-tenant>.accounts.ondemand.com` |
| `SCI_CLIENT_ID` | Client ID from the SCI application created in Step 1 (found under **Trust > Client Authentication**) |
| `JOULE_STUDIO_URL` | Joule Studio Deploy Service URL. Obtain it from Joule Studio under **User Settings > Develop > CLI Sign-in URL** (omit any query parameters), e.g. `https://<your-tenant>.studio.joule.cloud.sap/cli/v1` |

> **Important:** For each secret, set **Repository access** to **Selected repositories** and select only the repositories that are allowed to deploy. If the repository does not exist yet, add it to each secret's access list after creating it in Step 3.

---

## Step 3: Create a GitHub Repository and Connect Your Solution

### Create a GitHub Repository

1. Log in to GitHub and create a new repository.
2. Set the owner to your GitHub organization and the repository name to identify the solution.
3. Do not initialize the repository with a README.
4. Grant the repository access to the organization secrets required by this flow (listed in Step 2).

### Connect Your Solution to GitHub

Connect your solution from Joule Studio to the repository you just created, then push it.

Before running the pipeline, you need to add the following files to your repository manually:

```text
.github/workflows/deploy.yml
.github/actions/setup-jl/action.yml
.github/actions/token-fetch/action.yml
.github/actions/token-fetch/fetch.py
.github/actions/build/action.yml
.github/actions/deploy/action.yml
```

> **Reference:** A reference copy of the pipeline configuration is maintained in an external repository:
> `https://github.com/SAP-samples/lifecycle-operations-for-joule-studio/tree/main/github-oidc`

### Configure a Repository-Level Custom Subject

1. In your GitHub repository, go to **Settings > Actions > OIDC**.
2. Under **Subject claim**, clear **Use default template**.
3. Set **Subject claim template** to only:
   ```text
   repo
   ```
4. Select **Save subject claim**.

5. Select **Copy subject claim prefix** beside **Default subject claim prefix**. Use the copied value as the SCI **Subject** in the next section.


### Allow the Repository to Deploy in SCI

1. In the SCI administration console, open the application created in Step 1 and go to **Trust > Client Authentication**.

2. Add a federated trust entry with the following values:
   - **Description:** Optional
   - **Issuer Configuration:** Select **Manual Configuration**
   - **Issuer:** `https://token.actions.githubusercontent.com`
   - **JSON Web Key Set URI:** `https://token.actions.githubusercontent.com/.well-known/jwks`
   - **Refresh Interval:** 24 hours
   - **Subject:** Paste the value copied using **Copy subject claim prefix**. Depending on the repository's subject format, it will look like one of the following:
     ```text
     repo:my-org/my-repo
     ```

3. Select **Save**.

---

## Step 4: Run the Workflow

1. In your GitHub repository, go to **Actions** and select **Deploy to Joule Studio**.
2. Select **Run workflow**, choose the branch or tag you want to deploy, and start the workflow.

Once the workflow completes successfully, the solution is live in the productive environment.

### Pipeline Structure

**Build and deploy to Joule Studio** performs the following in order:

| Phase | What it does |
|---|---|
| Checkout | Checks out the selected branch or tag |
| Install CLI | Installs Node.js and the Joule Studio `jl` CLI |
| Fetch token | Requests a GitHub OIDC token with `id-token: write` and exchanges it for an SCI access token |
| Build | Runs `jl solution build` to validate and package the solution |
| Deploy | Runs `jl solution deploy --force` from the solution directory |

---

## Additional Resources

- [GitHub Actions documentation](https://docs.github.com/actions)
- [Using secrets in GitHub Actions](https://docs.github.com/actions/security-guides/using-secrets-in-github-actions)
- [GitHub OIDC subject customization](https://docs.github.com/en/actions/reference/security/oidc)

---

**Last Updated:** 2026-09-09
