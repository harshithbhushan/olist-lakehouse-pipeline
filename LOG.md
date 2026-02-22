# 30-Day Data Engineering Hard Reset: Olist Lakehouse

## Day 1: Environment & System Foundation
- **Goal:** Establish a production-grade local workstation.
- **Actions:**
    - Installed **Python 3.12.10** for library stability and **PowerShell 7** for automation.
    - Initialized **Monorepo structure**: `/dags`, `/dbt`, `/scripts`, `/data`, `/logs`, `/tests`.
    - Implemented **Zero-Trust Security**: Configured `.gitignore` to protect `.env` secrets and raw datasets.
- **Why:** Mirroring enterprise setups ensures that the transition from local development to cloud deployment is seamless.

## Day 2: Cloud Infrastructure & Safety Brakes
- **Goal:** Initialize Snowflake with cost-protection and security.
- **Actions:**
    - Provisioned **Snowflake Standard Edition** on AWS (us-east-1).
    - Created **Resource Monitor (`STUDENT_LIMIT`)**: Set a hard cap at 10 credits to prevent cost overruns.
    - Standardized warehouse settings: `OLIST_WH` (X-Small) with 60s auto-suspend.
- **Why:** In cloud engineering, "Resource Monitoring" is a Day 1 priority to manage OpEx (Operating Expenses).

## Day 3: RBAC & The Landing Zone
- **Goal:** Implement Role-Based Access Control and stage data.
- **Actions:**
    - Established **RBAC**: Created `TRANSFORMER_ROLE` to follow the Principle of Least Privilege.
    - Provisioned `OLIST_LAKEHOUSE` DB and `BRONZE` schema.
    - Initialized **Internal Stage (`raw_stage`)**: Created the landing zone for programmatic ingestion.
- **Why:** Separating roles prevents unauthorized access, and staging data allows for optimized bulk loading.
    - Added .gitignore, .env.example, LOG.md, README.md to GitHub so that the repo will know what to ignore to act as a 'Guard' against accidental data leaks.
- **Why:** .env.example is just a template so that future me and other users know that, a variable called SNOWFLAKE_USER is required to run the app. It contains only the keys but not the values.
    - Renaming the master branch to main branch using (-M = "Move/Rename") as per industry standard.
    - I was unable to push the branch to Github which means the local Git never successfully learned the address of your GitHub repo.
    - Fixed it after creating the repo on GitHub.


### ⚠️ Technical Challenges & Key Learnings
- **The Ownership Trap:** I discovered that creating an object (Schema/Stage) as `ACCOUNTADMIN` does not automatically give access to my service role (`TRANSFORMER_ROLE`).
    - *Fix:* I had to explicitly execute `GRANT OWNERSHIP` and switch roles (`USE ROLE TRANSFORMER_ROLE`) *before* creating the stage to ensure the pipeline role owned the infrastructure.
- **Idempotency:** Utilized `CREATE OR REPLACE` for all DDL statements to ensure the setup scripts can be re-run safely without crashing.


## Day 4: Programmatic Ingestion (The Bronze Layer)
- 