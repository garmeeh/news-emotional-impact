import os
import csv
import json
import time
from supabase import create_client, Client
from dotenv import load_dotenv

from postgrest.exceptions import APIError as PostgrestAPIError


# --- Configuration ---
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError(
        "SUPABASE_URL and SUPABASE_KEY (preferably SERVICE_ROLE_KEY) must be set in .env file."
    )

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

PAGE_SIZE = 1000  # Number of rows to fetch per call
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds

OUTPUT_DIR = "exported_datasets"
NEWS_ARTICLES_FILE = os.path.join(OUTPUT_DIR, "news_articles_dataset_export.csv")
SENTIMENTS_JOINED_FILE = os.path.join(
    OUTPUT_DIR, "news_article_sentiments_dataset_export.csv"
)


# --- Helper Functions ---
def call_supabase_rpc(sql_function_name, params):
    for attempt in range(MAX_RETRIES):
        try:
            # Parameters for RPC are passed as a dictionary
            response = supabase.rpc(sql_function_name, params).execute()

            # The execute() method will raise an exception (e.g., PostgrestAPIError)
            # if the RPC call itself results in an error from the database.
            # Thus, the explicit check for response.error is often not needed here
            # if relying on exception handling for PostgREST errors.

            return response.data
        except (
            PostgrestAPIError,
            ConnectionError,
            TimeoutError,
        ) as e:
            print(
                f"Supabase API error (attempt {attempt + 1}/{MAX_RETRIES}) calling {sql_function_name}: {e}"
            )
            if attempt < MAX_RETRIES - 1:
                print(f"Retrying in {RETRY_DELAY} seconds...")
                time.sleep(RETRY_DELAY)
            else:
                print(
                    f"Max retries reached for {sql_function_name}. Aborting this call."
                )
                raise
        except Exception as e:
            print(
                f"Unexpected error (attempt {attempt + 1}/{MAX_RETRIES}) calling {sql_function_name}: {e}"
            )
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
            else:
                print(
                    f"Max retries reached for {sql_function_name}. Aborting this call."
                )
                raise
    return None


def export_dataset(sql_function_name, output_filename):
    print(
        f"\n--- Exporting dataset via RPC '{sql_function_name}' to {output_filename} ---"
    )
    offset = 0
    first_batch = True
    total_rows_fetched = 0

    os.makedirs(os.path.dirname(output_filename), exist_ok=True)

    try:
        with open(output_filename, "w", newline="", encoding="utf-8") as csvfile:
            csv_writer = None
            while True:
                print(
                    f"Fetching rows for {sql_function_name}: offset={offset}, limit={PAGE_SIZE}"
                )

                rpc_params = {"page_limit": PAGE_SIZE, "page_offset": offset}

                try:
                    data = call_supabase_rpc(sql_function_name, rpc_params)
                except Exception as e:
                    print(
                        f"Failed to fetch data for {sql_function_name} at offset {offset} after retries. Error: {e}"
                    )
                    break  # Stop processing this dataset

                if (
                    data is None
                ):  # Should only happen if call_supabase_rpc returns None (which it shouldn't with re-raise)
                    print(
                        f"No data returned from RPC call for {sql_function_name} at offset {offset}. Stopping."
                    )
                    break

                if not data and offset > 0:  # No more data after the first page
                    print(
                        f"No more data received for {sql_function_name} at offset {offset}. Assuming end of dataset."
                    )
                    break

                if not data and offset == 0:  # No data at all
                    print(
                        f"Dataset from RPC '{sql_function_name}' appears to be empty."
                    )
                    break

                if first_batch:
                    if data:  # Ensure data is not empty before trying to get keys
                        headers = data[0].keys()
                        csv_writer = csv.DictWriter(csvfile, fieldnames=headers)
                        csv_writer.writeheader()
                        print(f"CSV Headers: {list(headers)}")
                        first_batch = False
                    else:
                        break

                if csv_writer:
                    for row in data:
                        # Convert array fields (like secondary_category_tag_names) to a JSON string
                        # The SQL function returns TEXT[] which supabase-py rpc converts to Python lists
                        for key, value in row.items():
                            if isinstance(value, list):
                                row[key] = json.dumps(
                                    value
                                )  # Store as JSON string in CSV
                            elif value is None:
                                row[key] = ""  # Replace None with empty string for CSV
                        csv_writer.writerow(row)

                    rows_in_batch = len(data)
                    total_rows_fetched += rows_in_batch
                    print(
                        f"Fetched and wrote {rows_in_batch} rows. Total so far: {total_rows_fetched}"
                    )

                if len(data) < PAGE_SIZE:
                    print(
                        f"Fetched {len(data)} rows, which is less than page size {PAGE_SIZE}. Assuming end of dataset."
                    )
                    break

                offset += PAGE_SIZE
                # time.sleep(0.1) # Optional small delay

    except Exception as e:
        print(f"An critical error occurred during export of {sql_function_name}: {e}")

    print(
        f"Finished exporting {sql_function_name}. Total rows: {total_rows_fetched}. Output: {output_filename}"
    )


# --- Main Execution ---
if __name__ == "__main__":
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    # Export News Articles
    export_dataset("get_news_articles_paginated", NEWS_ARTICLES_FILE)

    # Export Joined News Article Sentiments
    export_dataset("get_joined_sentiments_paginated", SENTIMENTS_JOINED_FILE)

    print("\nAll datasets exported.")
