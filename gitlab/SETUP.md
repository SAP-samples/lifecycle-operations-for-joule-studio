# GitLab Setup for Joule Studio

## Overview

Production deployment in Joule Studio uses GitLab as the promotion mechanism. A developer pushes their solution to a GitLab repository, and an administrator manually triggers a GitLab pipeline to deploy it to the productive environment. This manual trigger is the deliberate approval gate for production.

> **Note:** GitLab setup is only required once you are ready to promote a solution to production. It is not a prerequisite for building, testing, or running solutions in the development environment. Development deployments can be performed directly from Joule Studio. See [Deployment](https://help.sap.com/docs/business-ai-platform/joule-studio/deployment).

---

## Prerequisites

- Core Components, Joule, and Joule Studio are provisioned for both environments.
- Your organization has a GitLab license (GitLab.com or self-managed). The GitLab instance must be internet-accessible.
- You have administrator access to your SAP Cloud Identity Services (SCI) tenant.

---

## Step 1: Establish Trust Between SAP Cloud Identity Services and GitLab

Authentication between GitLab CI and Joule Studio uses the OAuth 2.0 client credentials grant. The pipeline exchanges a client ID and client secret for a Cloud Identity Services access token, which it then uses to call the Joule Studio solution management API.

### Create the Application

1. Log in to the SCI administration console at `https://<your-sci-tenant>.accounts.ondemand.com/admin`.

2. Go to **Applications & Resources** and select the **Applications** tile.

3. Select **Create** and fill in the dialog:
   - **Display Name:** Use a name that identifies your GitLab group, for example `gitlab.com/<your-group>`.
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
> - Before the secret expires, create a new secret and update the `SCI_CLIENT_ID` and `SCI_CLIENT_SECRET` variables in GitLab.
> - Treat both the client ID and client secret as credentials: do not commit them to the repository, and store them only as secured pipeline variables (see Step 2).

### Define a Dependency to the Joule Studio Application

1. Still on the **Trust** tab, under **Application APIs**, select **Dependencies**.

2. Select **Add** and fill in the dialog:
   - **Dependency Name:** `build`
   - **Application:** Search `Joule Studio` and find your Joule Studio application in the list.
   - **API:** Select `solution-deployment`

3. Select **Save**.

---

## Step 2: Configure CI/CD Variables

Set the following variables at the **GitLab group level** under **Group > Settings > CI/CD > Variables**. This way every repository in the group inherits them automatically.

> **Tip:** For tighter scoping, you can set these variables on a dedicated subgroup or on each individual project instead, under **Project > Settings > CI/CD > Variables**. Note that group-level variables are visible to every project in the group.

> **How inheritance works:** A project inherits variables from its parent group. If a project does not set `SCI_CLIENT_SECRET`, its pipeline automatically uses the group-level value. If the same variable is set at both levels, the project-level value wins. For example, a leftover or empty project-level `SCI_CLIENT_SECRET` silently overrides the correct group value, and the token exchange fails with `invalid_client`.

| Variable | Visibility | Description |
|---|---|---|
| `SCI_TENANT_URL` | Visible | Issuer URI of your SAP Cloud Identity Services tenant, e.g. `https://<your-tenant>.accounts.ondemand.com` |
| `SCI_CLIENT_ID` | **Masked and hidden** | Client ID from the SCI application created in Step 1 |
| `SCI_CLIENT_SECRET` | **Masked and hidden** | Client secret from the SCI application created in Step 1 |
| `JOULE_STUDIO_URL` | Visible | Joule Studio Deploy Service URL. Get it from Joule Studio under **User Settings > Develop > CLI Sign-in URL** (omit any query parameters), e.g. `https://<your-tenant>.studio.joule.cloud.sap/cli/v1` |

> **Important:** Mark `SCI_CLIENT_ID` and `SCI_CLIENT_SECRET` as **Masked and hidden** so their values are masked in job logs and cannot be read back from the GitLab UI after saving.
>
> Enable **Protect variable** and protect your default branch. This restricts the variables to pipelines running on protected branches or tags only. For example, a pipeline triggered on a feature branch cannot access `SCI_CLIENT_SECRET` — only a pipeline running on `main` (if `main` is protected) can.
>
> Leave **Expand variable reference** disabled (the default). When enabled, GitLab substitutes `$` references in the value — for example, if you have a variable `ENV=prod`, another variable with value `https://$ENV.example.com` becomes `https://prod.example.com`. For credentials this is harmful: a secret value like `/bCivB]aIdp$xV0St0` would become `/bCivB]aIdp` (the `$xV0St0` part is replaced with an empty string). Keep it off so the value is always passed as-is.

---

## Step 3: Create a GitLab Repository and Connect Your Solution

### Create a GitLab Repository

1. Log in to GitLab and create a new project.
2. Set the project name to identify the solution.
3. Do not initialize the repository with a README.

### Connect Your Solution to GitLab

Connect your solution from Joule Studio to the repository you just created, then push it.

> **Note:** The pipeline files are pushed only if they do not already exist in the repository. Joule Studio does not overwrite them, so you are free to customize the pipeline to fit your needs. If you delete the files and push again from Joule Studio, they are restored to the default template.

```
.gitlab-ci.yml
.gitlab/scripts/fetch.py
```

You can find reference templates for these files in the repository linked below.

> **Reference:** A reference copy of the pipeline configuration is maintained in an external repository:
> `https://github.com/SAP-samples/lifecycle-operations-for-joule-studio/tree/main/gitlab`

---

## Step 4: Run the Pipeline

1. In your GitLab repository, go to **Build > Pipelines**.
2. Select **New pipeline**.
3. Select branch `main` and select **Run pipeline**.

Once the pipeline completes successfully, the solution is live in the productive environment.

### Pipeline Structure

**Build and deploy to Joule Studio** performs the following in order:

| Phase | What it does |
|---|---|
| Setup CLI | Installs the `jl` CLI and prints its version |
| Fetch token | Runs `.gitlab/scripts/fetch.py` to exchange the client credentials for a short-lived SCI access token |
| Build | Runs `jl solution build` to validate and package the solution |
| Deploy | Runs `jl solution deploy --force` to upload and deploy the solution |

---

## Additional Resources

- [GitLab CI/CD Variables](https://docs.gitlab.com/ci/variables/)
- [GitLab Protected Branches](https://docs.gitlab.com/user/project/repository/branches/protected/)

---

**Last Updated:** 2026-09-09
