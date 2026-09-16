# Azure DevOps Setup for Joule Studio (Client Credentials)

## Overview

Production deployment in Joule Studio uses Azure Pipelines as the promotion mechanism. A developer pushes their solution to an Azure Repos repository, and an administrator manually triggers the deployment pipeline to deploy it to the productive environment. This manual trigger is the deliberate approval gate for production.

This setup uses **OAuth 2.0 client credentials** (client ID + client secret) to authenticate the pipeline against SAP Cloud Identity Services, storing the credentials as secured variables in Azure Pipelines (at project or pipeline level).

> **Note:** Azure DevOps setup is only required once you are ready to promote a solution to production. It is not a prerequisite for building, testing, or running solutions in the development environment. Development deployments can be performed directly from Joule Studio. See [Deployment](https://help.sap.com/docs/business-ai-platform/joule-studio/deployment).

---

## Prerequisites

- Core Components, Joule, and Joule Studio are provisioned for both environments.
- Your organization has an Azure DevOps account with Pipelines enabled for the project.
- You have administrator access to your SAP Cloud Identity Services (SCI) tenant.

---

## Step 1: Establish Trust Between SAP Cloud Identity Services and Azure DevOps

Authentication between Azure Pipelines and Joule Studio uses the OAuth 2.0 client credentials grant. The pipeline exchanges a client ID and client secret for a Cloud Identity Services access token, which it then uses to call the Joule Studio solution management API.

### Create the Application

1. Log in to the SCI administration console at `https://<your-sci-tenant>.accounts.ondemand.com/admin`.

2. Go to **Applications & Resources** and select the **Applications** tile.

3. Select **Create** and fill in the dialog:
   - **Display Name:** Use a name that identifies your Azure DevOps organization or project, for example `azure-devops/<your-org>/<your-project>`
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
> - Before the secret expires, create a new secret and update the `SCI_CLIENT_SECRET` variable in Azure DevOps.
> - Treat both the client ID and client secret as credentials: do not commit them to the repository, and store them only as secured pipeline variables (see Step 2).

### Define a Dependency to the Joule Studio Application

1. Still on the **Trust** tab, under **Application APIs**, select **Dependencies**.

2. Select **Add** and fill in the dialog:
   - **Dependency Name:** `build`
   - **Application:** Search `Joule Studio` and find your Joule Studio application in the list.
   - **API:** Select `solution-deployment`

3. Select **Save**.

---

## Step 2: Configure CI/CD Variables in Azure DevOps

Set the following variables in Azure DevOps. You can configure them at the **project level** (shared across all repositories in the project) or **pipeline level** (for a single repository/pipeline).

> **Note:** In Azure DevOps, a **Project** can contain multiple **Repositories**. Project-level variables are shared across all repositories in the project, while pipeline-level variables are specific to a single repository's pipeline.

### Option A: Configure Variables at Project Level

1. In Azure DevOps, navigate to your project.

2. Go to **Pipelines** → **Library**.

3. Select **+ Variable group** and create a group named `joule-studio-config`.

4. Add the following variables:

| Variable | Secret? | Description |
|---|---|---|
| `SCI_TENANT_URL` | No | Issuer URI of your SAP Cloud Identity Services tenant, e.g. `https://<your-tenant>.accounts.ondemand.com` or `https://<your-tenant>.accounts400.cloud.sap` |
| `SCI_CLIENT_ID` | **Yes** | Client ID from the SCI application created in Step 1 |
| `SCI_CLIENT_SECRET` | **Yes** | Client secret from the SCI application created in Step 1 |
| `JOULE_STUDIO_URL` | No | Joule Studio Deploy Service URL. Obtain it from Joule Studio under **User Settings > Develop > CLI Sign-in URL** (omit any query parameters), e.g. `https://api.dev.eu12.studio.joule.cloud.sap/api/v1` |

5. Mark both `SCI_CLIENT_ID` and `SCI_CLIENT_SECRET` as **secret** (lock icon) so their values are masked in build logs.

6. Click **Save** to create the variable group.

7. **Authorize the pipeline to use the variable group:**

   After you create or run the pipeline for the first time, return to **Pipelines** → **Library** → select your variable group → under **Pipeline permissions**, click **+** and authorize your pipeline to access this variable group.

8. **Reference the variable group in your pipeline YAML:**

   Add the following to your `deploy.yml`:

   ```yaml
   variables:
     - group: joule-studio-config
   ```

   > **Important:** The variable group name in the YAML file must match exactly the name you created in Step 3 above.

### Option B: Configure Variables in Pipeline UI

Alternatively, you can configure variables directly in the Pipeline's UI (recommended for simple setups):

> **Note:** If you haven't created a pipeline yet, see Step 4 for instructions on how to create one.

1. In Azure DevOps, navigate to **Pipelines** and select your pipeline.

2. Click **Edit** (top right).

3. Click **Variables** button (top right, or three dots `···` → Variables).

4. Click **New variable** and add each variable:

| Name | Secret? | Value |
|---|---|---|
| `SCI_TENANT_URL` | No | Issuer URI of your SAP Cloud Identity Services tenant, e.g. `https://<your-tenant>.accounts.ondemand.com` or `https://<your-tenant>.accounts400.cloud.sap` |
| `SCI_CLIENT_ID` | **Yes** | Client ID from the SCI application created in Step 1 |
| `SCI_CLIENT_SECRET` | **Yes** | Client secret from the SCI application created in Step 1 |
| `JOULE_STUDIO_URL` | No | Joule Studio Deploy Service URL. Obtain it from Joule Studio under **User Settings > Develop > CLI Sign-in URL** (omit any query parameters), e.g. `https://api.dev.eu12.studio.joule.cloud.sap/api/v1` |

5. Click **OK** after each variable, then **Save**.

> **Note:** These variables are stored in the Pipeline configuration and are not visible in the YAML file. They can be used directly in pipeline scripts without declaring them in the `variables:` section.

---

## Step 3: Create an Azure Repos Repository and Connect Your Solution

### Create an Azure Repos Repository

1. In your Azure DevOps project, go to **Repos** → **Files**.

2. Select **Initialize** or **Import repository** if this is a new project.

### Connect Your Solution to Azure Repos

Connect your solution from Joule Studio to the repository you just created, then push it. Pushing from Joule Studio will include the solution files (`solution.yaml`, `.build`, asset definitions).

### Create the Pipeline Configuration

You need to add the following file to your repository manually:

```
deploy.yml
```

The pipeline will:
1. Install the Joule Studio CLI
2. Exchange client credentials for an IAS access token
3. Deploy your solution

You can find a reference template for this file in the repository linked below.

> **Reference:** A complete pipeline template is available in this repository at:
> `azure/deploy.yml`
>
> The template includes detailed comments. You can copy it directly or customize it for your needs.
>
> A reference copy of the pipeline configuration is also maintained in an external repository:
> `https://github.com/SAP-samples/lifecycle-operations-for-joule-studio/tree/main/azure`

---

## Step 4: Run the Pipeline

1. In Azure DevOps, go to **Pipelines** → **Pipelines**.
2. Select **New pipeline** (if first time) or select your existing pipeline.
3. Select **Azure Repos Git** and choose your repository.
4. Select **Existing Azure Pipelines YAML file** and choose `/deploy.yml`.
5. Select **Run pipeline**.
6. Confirm the branch (typically `main`) and select **Run**.

Once the pipeline completes successfully, the solution is live in the productive environment.

### Pipeline Structure

 **Deploy Solution to Production** performs the following in order:

| Phase | What it does |
|---|---|
| Checkout | Checks out the solution repository |
| Setup Node.js | Installs Node.js 24, required by the Joule Studio CLI |
| Install CLI | Installs the Joule Studio `jl` CLI via npm |
| Get IAS token | Exchanges client credentials for an IAS access token via OAuth 2.0 client credentials grant |
| Deploy | Runs `jl solution deploy --force` to build, upload, and deploy the solution |

---

## Additional Resources

- [Azure DevOps Pipeline Variables](https://learn.microsoft.com/en-us/azure/devops/pipelines/process/variables)
- [SAP Cloud Identity Services Documentation](https://help.sap.com/docs/identity-authentication)
- [Joule Studio Deployment Guide](https://help.sap.com/docs/business-ai-platform/joule-studio/deployment)

---

**Last Updated:** 2026-09-09
