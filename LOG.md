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


## Day 4: Programmatic Ingestion (The Bridge)
- **Goal:** Build a secure, automated ingestion script to move raw local data to the Snowflake cloud stage.
- **Actions:**
    - Configured `python-dotenv` to securely inject credentials into the environment at runtime, maintaining Zero-Trust architecture.
    - Engineered `scripts/load_bronze.py` using the `snowflake-connector-python` library.
    - Executed Snowflake's native `PUT` command to iterate over the local `/data` directory and upload 9 raw CSV files.
- **Why:** Manual uploads via the UI are unscalable. Programmatic ingestion via the `PUT` command allows for automatic file compression (gzip) and sets the foundation for future orchestration (Airflow).

### ⚠️ Technical Challenges & Key Learnings
- **Variable Scope and Consistency:** Encountered a `NameError` due to inconsistent variable naming (`data` vs `data_dir`). It reinforced that Python is entirely literal; variable declarations must exactly match their execution calls.
- **Execution Guards:** Discovered the risk of duplicate `if __name__ == "__main__":` blocks. A script should only have one entry point at the absolute end of the file to prevent duplicate execution loops and memory leaks.
- **Tooling vs. Files (`dotenv` vs `.env`):** Solidified the difference between a static file and an active tool. `.env` is just a text file acting as a safe for secrets; `python-dotenv` is the necessary "locksmith" tool Python uses to actually open it and load variables into memory securely.
- **Identity Decoupling (Custom vs. System Roles):** Reaffirmed the "why" behind custom RBAC. We explicitly created `TRANSFORMER_ROLE` instead of using default system roles (`ACCOUNTADMIN`) to decouple the "identity that pays the bill" from the "identity that runs the pipeline," enforcing the Principle of Least Privilege and minimizing the blast radius of any potential errors. (The Principle of Least Privilege (PoLP) AND maintaining the hierarchy)