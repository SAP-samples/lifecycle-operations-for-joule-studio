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

---

## Step 1: Create an Application in SAP Cloud Identity Services

Authentication between GitHub Actions and Joule Studio uses the OAuth 2.0 client credentials grant. The workflow exchanges a client ID and client secret for a Cloud Identity Services access token, which it then uses to call the Joule Studio solution management API.

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

### Obtain the Client ID and Create a Client Secret

1. On the **Trust** tab, under **Application APIs**, select **Client Authentication**.

2. **Create a client secret:**
   - Under the **Secrets** section, select **Add**
   - In the dialog:
     - **Description:** Enter a meaningful description
     - **Expire in:** Select an expiration period (e.g., 1 year, 2 years, or never)
       - ⚠️ **Important:** Note the expiration date. You must rotate the secret before it expires, or the pipeline will fail.
     - Under **API Access**, select **OpenID**
       - This is the scope required for the token exchange used by the pipeline
       - The other options (**Application**, **Application Users**, **AMS Policies**) are not required
   - Select **Save**

3. **Copy the client ID and client secret from the confirmation dialog:**
   - A dialog will appear showing both:
     - **Client ID**
     - **Client Secret** (the newly generated secret)
   - **Copy both values immediately** — the client secret is displayed only once
   - You will need them as `SCI_CLIENT_ID` and `SCI_CLIENT_SECRET` CI/CD variables in Step 2
   - Select **Close** to dismiss the dialog

> **Important:**
> - The client secret is displayed only once at creation time. If it is lost, you must generate a new secret.
> - Before the secret expires, create a new secret and update the `SCI_CLIENT_ID` and `SCI_CLIENT_SECRET` variables in Github.
> - Treat both the client ID and client secret as credentials: do not commit them to the repository, and store them only as secured pipeline variables (see Step 2).

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
| `SCI_CLIENT_ID` | Client ID from the SCI application created in Step 1 |
| `SCI_CLIENT_SECRET` | Client secret from the SCI application created in Step 1 |
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

> **Note:** The pipeline files are pushed only if they do not already exist in the repository. Joule Studio does not overwrite them, so you are free to customize the pipeline to fit your needs. If you delete the files and push again from Joule Studio, they are restored to the default template.

```text
.github/workflows/deploy.yml
.github/actions/setup-jl/action.yml
.github/actions/token-fetch/action.yml
.github/actions/token-fetch/fetch.py
.github/actions/build/action.yml
.github/actions/deploy/action.yml
```

> **Reference:** A reference copy of the pipeline configuration is maintained in an external repository:
> `https://github.com/SAP-samples/lifecycle-operations-for-joule-studio/tree/main/azure`

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
| Fetch token | Exchanges the SCI client ID and client secret for an SCI access token |
| Build | Runs `jl solution build` to validate and package the solution |
| Deploy | Runs `jl solution deploy --force` from the solution directory |

---

## Additional Resources

- [GitHub Actions documentation](https://docs.github.com/actions)
- [Using secrets in GitHub Actions](https://docs.github.com/actions/security-guides/using-secrets-in-github-actions)

---

**Last Updated:** 2026-09-09
