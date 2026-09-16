# Bitbucket Setup for Joule Studio

## Overview

Production deployment in Joule Studio uses Bitbucket Pipelines as the promotion mechanism. A developer pushes their solution to a Bitbucket repository, and an administrator manually triggers the deployment pipeline to deploy it to the productive environment. This manual trigger is the deliberate approval gate for production.

> **Note:** Bitbucket setup is only required once you are ready to promote a solution to production. It is not a prerequisite for building, testing, or running solutions in the development environment. Development deployments can be performed directly from Joule Studio. See [Deployment](https://help.sap.com/docs/business-ai-platform/joule-studio/deployment).

---

## Prerequisites

- Core Components, Joule, and Joule Studio are provisioned for both environments.
- Your organization has a Bitbucket Cloud account, and Bitbucket Pipelines is enabled for the repository. The Bitbucket instance must be internet-accessible.
- You have administrator access to your SAP Cloud Identity Services (SCI) tenant.

---

## Step 1: Establish Trust Between SAP Cloud Identity Services and Bitbucket

Authentication between Bitbucket Pipelines and Joule Studio uses the OAuth 2.0 client credentials grant. The pipeline exchanges a client ID and client secret for a Cloud Identity Services access token, which it then uses to call the Joule Studio solution management API.

### Create the Application

1. Log in to the SCI administration console at `https://<your-sci-tenant>.accounts.ondemand.com/admin`.

2. Go to **Applications & Resources** and select the **Applications** tile.

3. Select **Create** and fill in the dialog:
   - **Display Name:** Use a name that identifies your Bitbucket workspace or repository, for example `bitbucket/<your-workspace>`.
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
> - Before the secret expires, create a new secret and update the `SCI_CLIENT_ID` and `SCI_CLIENT_SECRET` variables in Bitbucket.
> - Treat both the client ID and client secret as credentials: do not commit them to the repository, and store them only as secured pipeline variables (see Step 2).

### Define a Dependency to the Joule Studio Application

1. Still on the **Trust** tab, under **Application APIs**, select **Dependencies**.

2. Select **Add** and fill in the dialog:
   - **Dependency Name:** `build`
   - **Application:** Search `Joule Studio` and find your Joule Studio application in the list.
   - **API:** Select `solution-deployment`

3. Select **Save**.

---

## Step 2: Configure Repository Variables in Bitbucket

Set the following variables at the **repository level**, under **Repository settings > Pipelines > Repository variables**.

> **Tip:** You can also set these variables at the **workspace level** under **Profile > Workspace settings > Pipelines > Workspace variables**. Note that workspace-level variables are visible to all repositories in the workspace.

| Variable | Secured | Description |
|---|---|---|
| `SCI_TENANT_URL` | No | Issuer URI of your SAP Cloud Identity Services tenant, e.g. `https://<your-tenant>.accounts.ondemand.com` |
| `SCI_CLIENT_ID` | **Yes** | Client ID from the SCI application created in Step 1 |
| `SCI_CLIENT_SECRET` | **Yes** | Client secret from the SCI application created in Step 1 |
| `JOULE_STUDIO_URL` | No | Joule Studio Deploy Service URL. Obtain it from Joule Studio under **User Settings > Develop > CLI Sign-in URL** (omit any query parameters), e.g. `https://<your-tenant>.studio.joule.cloud.sap/cli/v1` |

> **Important:** Mark `SCI_CLIENT_ID` and `SCI_CLIENT_SECRET` as **Secured** so their values are masked in the build logs and cannot be read back from the Bitbucket UI.

---

## Step 3: Create a Bitbucket Repository and Connect Your Solution

### Create a Bitbucket Repository

1. Log in to Bitbucket and create a new repository.
2. Set the repository name to identify the solution.
3. Do not initialize the repository with a README.

### Connect Your Solution to Bitbucket

Connect your solution from Joule Studio to the repository you just created, then push it.

> **Note:** The pipeline files are pushed only if they do not already exist in the repository. Joule Studio does not overwrite them, so you are free to customize the pipeline to fit your needs. If you delete the files and push again from Joule Studio, they are restored to the default template.

```
bitbucket-pipelines.yml
.bitbucket/scripts/fetch.py
```

You can find reference templates for these files in the repository linked below.

> **Reference:** A reference copy of the pipeline configuration is maintained in an external repository:
> `https://github.com/SAP-samples/lifecycle-operations-for-joule-studio/tree/main/bitbucket`

---

## Step 4: Run the Pipeline

1. In your Bitbucket repository, go to **Pipelines**.
2. Select **Run pipeline**.
3. Select branch `main`, choose the custom pipeline **`deploy-to-joule-studio`**, and select **Run**.

Once the pipeline completes successfully, the solution is live in the productive environment.

### Pipeline Structure
**Build and deploy to Joule Studio** performs the following in order:

| Phase | What it does |
|---|---|
| Install CLI | Installs the Joule Studio `jl` CLI |
| Fetch token | Runs `.bitbucket/scripts/fetch.py` to exchange the client credentials for an SCI access token |
| Build | Runs `jl solution build` to create a solution zip archive |
| Deploy | Runs `jl solution deploy --force` to upload and deploy the solution |


---

## Additional Resources

- [Bitbucket Variables and Secrets](https://support.atlassian.com/bitbucket-cloud/docs/variables-and-secrets/)
- [Build, Test, and Deploy with Pipelines](https://support.atlassian.com/bitbucket-cloud/docs/build-test-and-deploy-with-pipelines/)

---

**Last Updated:** 2026-09-09
