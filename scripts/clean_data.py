import pandas as pd  # type: ignore
from datetime import datetime
import os

# Define constants
BASE_DIR = "exported_datasets"
SENTIMENTS_FILE = os.path.join(BASE_DIR, "news_article_sentiments_dataset_export.csv")
ARTICLES_FILE = os.path.join(BASE_DIR, "news_articles_dataset_export.csv")

CLEANED_SENTIMENTS_FILE = os.path.join(
    BASE_DIR, "news_article_sentiments_dataset_cleaned.csv"
)
CLEANED_ARTICLES_FILE = os.path.join(BASE_DIR, "news_articles_dataset_cleaned.csv")

LOG_FILE = "log.txt"

# Cutoff date if needed
CUTOFF_DATE_STR = "2020-01-01 00:00:00"
CUTOFF_DATETIME = pd.to_datetime(CUTOFF_DATE_STR).tz_localize("UTC")

CHUNK_SIZE = 10000  # Process 10,000 rows at a time

# Ensure the output directory exists
os.makedirs(BASE_DIR, exist_ok=True)


def log_message(message: str) -> None:
    """Appends a message to the log file and prints it."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{now}] {message}"
    print(log_entry)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_entry + "\n")


if __name__ == "__main__":
    # Clear previous log file
    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)
    log_message("Starting data cleaning process.")

    # --- Step 0: Collect all unique news_article_ids from the original sentiments dataset ---
    log_message(
        f"Pre-processing: Collecting all news_article_ids from original {SENTIMENTS_FILE}..."
    )
    ids_in_original_sentiments: set[str] = set()
    sentiments_file_existed_for_id_collection = False
    try:
        if os.path.exists(SENTIMENTS_FILE):
            sentiments_file_existed_for_id_collection = True
            for i, chunk in enumerate(
                pd.read_csv(
                    SENTIMENTS_FILE,
                    chunksize=CHUNK_SIZE,
                    usecols=["news_article_id"],
                    dtype={
                        "news_article_id": object
                    },  # Read as object, then convert to str
                    low_memory=False,
                )
            ):
                log_message(
                    f"  Reading news_article_ids from original {SENTIMENTS_FILE} (chunk {i+1})"
                )
                ids_in_original_sentiments.update(
                    chunk["news_article_id"].dropna().astype(str).unique()
                )
            log_message(
                f"Found {len(ids_in_original_sentiments)} unique news_article_ids in original {SENTIMENTS_FILE}."
            )
        else:
            log_message(
                f"INFO: Original {SENTIMENTS_FILE} not found. Cannot collect IDs for cross-referencing articles."
            )

    except pd.errors.EmptyDataError:
        sentiments_file_existed_for_id_collection = True  # It existed but was empty
        log_message(
            f"WARNING: Original {SENTIMENTS_FILE} is empty. No article IDs to cross-reference."
        )
    except Exception as e:
        sentiments_file_existed_for_id_collection = True
        log_message(
            f"ERROR: An unexpected error occurred while pre-reading IDs from {SENTIMENTS_FILE}: {e}"
        )

    # --- Step 1: Clean sentiments data ---
    log_message(f"Processing {SENTIMENTS_FILE} for date-based cleaning...")
    sentiments_header_written = False
    total_sentiments_processed = 0
    total_sentiments_written = 0
    total_sentiments_removed_invalid_date = 0
    total_sentiments_removed_by_date_filter = 0

    if not os.path.exists(SENTIMENTS_FILE):
        log_message(
            f"INFO: {SENTIMENTS_FILE} not found. Skipping sentiment data cleaning."
        )
    else:
        try:
            for i, chunk in enumerate(
                pd.read_csv(SENTIMENTS_FILE, chunksize=CHUNK_SIZE, low_memory=False)
            ):
                original_rows = len(chunk)
                total_sentiments_processed += original_rows
                log_message(
                    f"  Processing chunk {i+1} of {SENTIMENTS_FILE} with {original_rows} rows for sentiment cleaning."
                )

                chunk["article_publish_date"] = pd.to_datetime(
                    chunk["article_publish_date"], errors="coerce", utc=True
                )

                chunk_with_valid_dates = chunk.dropna(subset=["article_publish_date"])
                rows_with_invalid_dates = original_rows - len(chunk_with_valid_dates)
                total_sentiments_removed_invalid_date += rows_with_invalid_dates

                chunk_after_date_filter = chunk_with_valid_dates[
                    chunk_with_valid_dates["article_publish_date"] >= CUTOFF_DATETIME
                ]
                rows_removed_by_date = len(chunk_with_valid_dates) - len(
                    chunk_after_date_filter
                )
                total_sentiments_removed_by_date_filter += rows_removed_by_date

                if rows_with_invalid_dates > 0:
                    log_message(
                        f"    {rows_with_invalid_dates} rows removed from chunk due to invalid date format in 'article_publish_date'."
                    )
                if rows_removed_by_date > 0:
                    log_message(
                        f"    {rows_removed_by_date} rows removed from chunk due to publish date before {CUTOFF_DATE_STR} UTC."
                    )

                if not chunk_after_date_filter.empty:
                    if not sentiments_header_written:
                        chunk_after_date_filter.to_csv(
                            CLEANED_SENTIMENTS_FILE, index=False, mode="w", header=True
                        )
                        sentiments_header_written = True
                        log_message(f"    Writing header to {CLEANED_SENTIMENTS_FILE}")
                    else:
                        chunk_after_date_filter.to_csv(
                            CLEANED_SENTIMENTS_FILE, index=False, mode="a", header=False
                        )
                    total_sentiments_written += len(chunk_after_date_filter)
                    log_message(
                        f"    {len(chunk_after_date_filter)} cleaned sentiment rows written to {CLEANED_SENTIMENTS_FILE} (chunk {i+1})."
                    )
                elif original_rows > 0:  # only log if there were rows to begin with
                    log_message(
                        f"    No sentiment rows left in chunk {i+1} after date filtering."
                    )
            log_message(f"Finished cleaning {SENTIMENTS_FILE}. Summary:")
            log_message(f"  Total rows processed: {total_sentiments_processed}")
            log_message(
                f"  Total rows removed due to invalid date format: {total_sentiments_removed_invalid_date}"
            )
            log_message(
                f"  Total rows removed due to date filter: {total_sentiments_removed_by_date_filter}"
            )
            log_message(f"  Total cleaned rows written: {total_sentiments_written}")

        except pd.errors.EmptyDataError:
            log_message(
                f"INFO: {SENTIMENTS_FILE} is empty. No sentiment data to clean."
            )
        except Exception as e:
            log_message(
                f"ERROR: An unexpected error occurred while cleaning {SENTIMENTS_FILE}: {e}"
            )

    # --- Step 2: Clean articles data ---
    log_message(f"Processing {ARTICLES_FILE} for cleaning...")
    articles_header_written = False
    total_articles_processed = 0
    total_articles_written = 0
    total_articles_removed_invalid_date = 0
    total_articles_removed_by_date_filter = 0
    total_articles_removed_by_id_filter = 0

    if not os.path.exists(ARTICLES_FILE):
        log_message(
            f"INFO: {ARTICLES_FILE} not found. Skipping articles data cleaning."
        )
    else:
        try:
            for i, chunk in enumerate(
                pd.read_csv(ARTICLES_FILE, chunksize=CHUNK_SIZE, low_memory=False)
            ):
                original_rows = len(chunk)
                total_articles_processed += original_rows
                log_message(
                    f"  Processing chunk {i+1} of {ARTICLES_FILE} with {original_rows} rows for article cleaning."
                )

                chunk["publish_date"] = pd.to_datetime(
                    chunk["publish_date"], errors="coerce", utc=True
                )

                chunk_with_valid_dates = chunk.dropna(subset=["publish_date"])
                rows_with_invalid_dates = original_rows - len(chunk_with_valid_dates)
                total_articles_removed_invalid_date += rows_with_invalid_dates

                chunk_after_date_filter = chunk_with_valid_dates[
                    chunk_with_valid_dates["publish_date"] >= CUTOFF_DATETIME
                ]
                rows_removed_by_date = len(chunk_with_valid_dates) - len(
                    chunk_after_date_filter
                )
                total_articles_removed_by_date_filter += rows_removed_by_date

                if rows_with_invalid_dates > 0:
                    log_message(
                        f"    {rows_with_invalid_dates} article rows removed from chunk due to invalid date format in 'publish_date'."
                    )
                if rows_removed_by_date > 0:
                    log_message(
                        f"    {rows_removed_by_date} article rows removed from chunk due to publish date before {CUTOFF_DATE_STR} UTC."
                    )

                # Filter by article IDs present in the *original* sentiments dataset
                rows_before_id_filter = len(chunk_after_date_filter)
                chunk_after_id_filter = chunk_after_date_filter  # Default to keep if sentiments file wasn't processed for IDs
                current_chunk_removed_by_id = 0

                if (
                    sentiments_file_existed_for_id_collection
                ):  # Only filter if we attempted to get IDs from sentiments
                    if not ids_in_original_sentiments:
                        log_message(
                            f"    Note: Original {SENTIMENTS_FILE} provided no IDs (empty or all NaNs). All articles in this chunk will be removed by ID filter unless it was not found."
                        )

                    filtered_chunk = chunk_after_date_filter[
                        chunk_after_date_filter["id"]
                        .astype(str)
                        .isin(ids_in_original_sentiments)
                    ]
                    current_chunk_removed_by_id = rows_before_id_filter - len(
                        filtered_chunk
                    )
                    chunk_after_id_filter = filtered_chunk
                    if current_chunk_removed_by_id > 0:
                        log_message(
                            f"    {current_chunk_removed_by_id} article rows removed from chunk because their 'id' was not found in the *original* {SENTIMENTS_FILE} data."
                        )
                else:  # sentiments_file_existed_for_id_collection is False
                    log_message(
                        f"    Skipping article 'id' filtering based on sentiments as original {SENTIMENTS_FILE} was not found during ID collection phase."
                    )

                total_articles_removed_by_id_filter += current_chunk_removed_by_id

                if not chunk_after_id_filter.empty:
                    if not articles_header_written:
                        chunk_after_id_filter.to_csv(
                            CLEANED_ARTICLES_FILE, index=False, mode="w", header=True
                        )
                        articles_header_written = True
                        log_message(f"    Writing header to {CLEANED_ARTICLES_FILE}")
                    else:
                        chunk_after_id_filter.to_csv(
                            CLEANED_ARTICLES_FILE, index=False, mode="a", header=False
                        )
                    total_articles_written += len(chunk_after_id_filter)
                    log_message(
                        f"    {len(chunk_after_id_filter)} cleaned article rows written to {CLEANED_ARTICLES_FILE} (chunk {i+1})."
                    )
                elif original_rows > 0:
                    log_message(
                        f"    No article rows left in chunk {i+1} after all filters."
                    )
            log_message(f"Finished cleaning {ARTICLES_FILE}. Summary:")
            log_message(f"  Total rows processed: {total_articles_processed}")
            log_message(
                f"  Total rows removed due to invalid date format: {total_articles_removed_invalid_date}"
            )
            log_message(
                f"  Total rows removed due to date filter: {total_articles_removed_by_date_filter}"
            )
            log_message(
                f"  Total rows removed due to ID filter (not in original sentiments): {total_articles_removed_by_id_filter}"
            )
            log_message(f"  Total cleaned rows written: {total_articles_written}")

        except pd.errors.EmptyDataError:
            log_message(f"INFO: {ARTICLES_FILE} is empty. No article data to clean.")
        except Exception as e:
            log_message(
                f"ERROR: An unexpected error occurred while cleaning {ARTICLES_FILE}: {e}"
            )

    log_message("Data cleaning process finished.")
