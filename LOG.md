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
- **Environment Synchronization:** Discovered that VS Code's visual linter (Pylance) and the execution terminal can operate on entirely different Python interpreters. Resolved false-positive "missing import" warnings by aligning the IDE's interpreter with the active environment.


## Day 5: Transformation Engine Foundation (dbt)
- **Goal:** Initialize the data build tool (dbt) and securely connect it to Snowflake without hardcoding credentials.
- **Actions:**
    - Established a Python virtual environment (`venv`) to quarantine project dependencies and avoid system-wide version conflicts.
    - Configured the project brain (`dbt_project.yml`) to define the Medallion materialization strategy (Bronze as views, Silver/Gold as tables).
    - Engineered `profiles.yml` using Jinja templating `{{ env_var() }}` to dynamically inject credentials from the `.env` file at runtime.
    - Successfully validated the connection using `dotenv run -- dbt debug`.

### ⚠️ Technical Challenges & Key Learnings
- **The YAML Whitespace Trap:** Learned that YAML files are ruthlessly strict about indentation. A single misplaced space or misaligned key will break the entire configuration.
- **Virtual Environments & IDE Sync:** Reinforced that VS Code's terminal and its background linters/extensions can sometimes fall out of sync. Trusting the terminal prompt (`(venv)`) is the ultimate source of truth.
- **PowerShell Encoding Traps:** Learned that using `echo > filename` in PowerShell can secretly encode files in UTF-16, which causes parsing errors in `dbt`. Adopted `New-Item` as the standard CLI method for clean file creation.
- **Jinja Templating for Security:** Introduced Jinja syntax (`{{ env_var() }}`) within configuration files. This acts as a dynamic placeholder, allowing the pipeline to fetch secrets at runtime and immediately drop them, rather than violating Zero-Trust by hardcoding passwords.
- **Architectural Efficiency (Direct Stage Querying):** Made an architectural decision to bypass the traditional `sources.yml` setup. Because Snowflake's engine is powerful enough to query compressed `.gz` files directly from an internal stage (`@raw_stage`), we can skip building intermediate Bronze tables entirely, optimizing both storage and compute.


## Day 6: The Silver Layer (Staging)
- **Goal:** Build the first transformational dbt model to clean raw Bronze data directly from the Snowflake stage.
- **Actions:**
    - Engineered a Snowflake `FILE FORMAT` to parse compressed `.csv.gz` files and automatically handle null string conversions.
    - Wrote `stg_orders.sql`, querying directly from `@raw_stage` using positional `$1` selection and explicit type casting.
    - Successfully materialized `SILVER.stg_orders` (99k+ rows) using the `-s` (select) flag in dbt.

### ⚠️ Technical Challenges & Key Learnings
- **RBAC Enforcement (Zero-Trust):** Encountered a `003001 (42501): SQL access control error`. Diagnosed this not as a code bug, but as the security architecture working correctly. `TRANSFORMER_ROLE` was blocked from creating tables until explicitly granted `ALL PRIVILEGES` on the `SILVER` schema by `ACCOUNTADMIN`.
- **Snowflake Delimiter Strictness:** Learned that Snowflake's parser can conflict with itself if `RECORD_DELIMITER` is explicitly set to `\n` alongside `FIELD_DELIMITER`. Removed the redundant row delimiter to rely on Snowflake's default engine, resolving the `001019 (22023)` compilation error.
- **dbt Pathing Automation:** Automated dbt's profile and project directory paths using `.env` variables (`DBT_PROFILES_DIR` and `DBT_PROJECT_DIR`) to cleanly eliminate repetitive CLI flags.
- **Schema-on-Read Architecture:** Implemented a Schema-on-Read paradigm. Instead of forcing raw data into a rigid, pre-defined table beforehand (Schema-on-Write), the structural definition (column names and explicit data types) was applied dynamically at the exact moment the raw `.gz` file was queried from the stage.
- **Common Table Expressions (CTEs):** Utilized the `WITH` clause to create modular, readable transformation logic. By staging the raw extraction in a temporary result set before executing the final `SELECT`, this established a clean, standard pattern for future complex transformations.
- **Named Argument Syntax (`=>`):** Leveraged Snowflake's parameter passing syntax. Used the `=>` operator to explicitly bind the custom `FILE_FORMAT` ruleset to the stage query, guaranteeing the raw data was parsed precisely according to the engineered CSV rules.