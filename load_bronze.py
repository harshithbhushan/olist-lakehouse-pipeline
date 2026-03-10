import os
import snowflake.connector
from dotenv import load_dotenv

def get_snowflake_connection():
    """Establishing a secure connection to Snowflake using environment variables."""
    # 1. Load the hidden credentials from the .env file
    load_dotenv()

    # 2. Establish the connection
    print("Initiating Snowflake connection...")
    conn = snowflake.connector.connect(
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        schema=os.getenv("SNOWFLAKE_SCHEMA"),
        role="TRANSFORMER_ROLE"
    )    
    print("Snowflake connection established successfully.")
    return conn


def upload_data_to_stage(conn):
    """Uploads all data from the local data directory to the snowflake stage."""
    print("Starting file upload process...")

    # 1. Defining the path
    data_dir = os.getenv("LOCAL_DATA_PATH")
    stage_name = "@OLIST_LAKEHOUSE.BRONZE.raw_stage"

    # 2. Opening the 'Cursor' (The object that actually executes SQL commands)
    cursor = conn.cursor()

    try: 
        # 3. Looping through files in the data directory and uploading them to the stage
        for filename in os.listdir(data_dir):
            if filename.endswith(".csv"):
                file_path = os.path.join(data_dir, filename)

                #Windows path fix: Snowflake expects forward slashes, so we replace backslashes with forward slashes
                abs_file_path = os.path.abspath(file_path).replace('\\', '/')
                
                print(f"Uploading {filename} to stage...")

                # 4. Execute the PUT command to upload the file to the stage
                put_query = f"PUT file://{abs_file_path} {stage_name} AUTO_COMPRESS=TRUE;"
                cursor.execute(put_query)
        
        print("All files successfully staged in snowflake.")

    except Exception as e:
        print(f"Upload failed: {e}")

    finally:
        # Always close the cursor, even if it fails
        cursor.close()

# The Execution Guard (modularity and security best practice)
if __name__ == "__main__":
    conn = get_snowflake_connection()
    # Calling the new upload function before closing the connection
    upload_data_to_stage(conn)
    conn.close()
    print("Connection closed successfully.")   
