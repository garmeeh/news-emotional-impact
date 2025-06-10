import pandas as pd  # type: ignore
import os
from datetime import datetime
from typing import Set, Tuple, List

BASE_DIR = "exported_datasets"
LOG_FILE = "deduplication_log.txt"
CHUNK_SIZE = 10000

SENTIMENTS_FILE = os.path.join(BASE_DIR, "news_article_sentiments_dataset_cleaned.csv")
ARTICLES_FILE = os.path.join(BASE_DIR, "news_articles_dataset_cleaned.csv")

FINAL_SENTIMENTS_FILE = os.path.join(
    BASE_DIR, "news_article_sentiments_dataset_final.csv"
)
FINAL_ARTICLES_FILE = os.path.join(BASE_DIR, "news_articles_dataset_final.csv")


def log_message(message: str) -> None:
    """Appends a message to the log file and prints it."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{now}] {message}"
    print(log_entry)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_entry + "\n")


def deduplicate_csv(input_path: str, output_path: str, key_columns: List[str]) -> None:
    """
    Deduplicates a CSV file based on key columns, processing in chunks.
    It keeps the first occurrence of each unique key combination.
    """
    log_message(
        f"Starting deduplication for {input_path} on columns: {', '.join(key_columns)}"
    )

    if not os.path.exists(input_path):
        log_message(f"INFO: Input file not found: {input_path}. Skipping.")
        return

    seen_keys: Set[Tuple] = set()
    header_written = False
    total_processed = 0
    total_written = 0

    try:
        for i, chunk in enumerate(
            pd.read_csv(input_path, chunksize=CHUNK_SIZE, low_memory=False)
        ):
            original_rows = len(chunk)
            total_processed += original_rows
            log_message(
                f"  Processing chunk {i+1} of {input_path} with {original_rows} rows."
            )

            # Drop duplicates within the chunk itself first
            chunk.drop_duplicates(subset=key_columns, keep="first", inplace=True)

            # Identify rows with keys that have already been seen in previous chunks
            # Make sure key columns are handled as strings to avoid type issues in tuples
            chunk_keys = chunk[key_columns].astype(str).apply(tuple, axis=1)
            is_seen = chunk_keys.isin(seen_keys)

            new_rows_chunk = chunk[~is_seen]

            # Add the new, unique keys from this chunk to our master set
            new_keys_to_add = set(chunk_keys[~is_seen])
            seen_keys.update(new_keys_to_add)

            if not new_rows_chunk.empty:
                if not header_written:
                    new_rows_chunk.to_csv(
                        output_path, index=False, mode="w", header=True
                    )
                    header_written = True
                    log_message(f"    Writing header to {output_path}")
                else:
                    new_rows_chunk.to_csv(
                        output_path, index=False, mode="a", header=False
                    )

                rows_written = len(new_rows_chunk)
                total_written += rows_written
                log_message(
                    f"    {rows_written} unique rows written to {output_path} (chunk {i+1})."
                )
            else:
                log_message(f"    No new unique rows found in chunk {i+1}.")

        log_message(f"Finished deduplicating {input_path}. Summary:")
        log_message(f"  Total rows processed: {total_processed}")
        log_message(f"  Total unique rows written: {total_written}")
        log_message(
            f"  Total duplicate rows removed: {total_processed - total_written}"
        )

    except pd.errors.EmptyDataError:
        log_message(f"INFO: {input_path} is empty. No data to deduplicate.")
    except KeyError as e:
        log_message(
            f"ERROR: A key column was not found: {e}. Please check the CSV header."
        )
    except Exception as e:
        log_message(
            f"ERROR: An unexpected error occurred while processing {input_path}: {e}"
        )


if __name__ == "__main__":
    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)
    log_message("Starting data deduplication process.")

    # 1. Deduplicate News Articles
    deduplicate_csv(
        input_path=ARTICLES_FILE,
        output_path=FINAL_ARTICLES_FILE,
        key_columns=["title", "source"],
    )

    # 2. Deduplicate News Article Sentiments
    deduplicate_csv(
        input_path=SENTIMENTS_FILE,
        output_path=FINAL_SENTIMENTS_FILE,
        key_columns=["article_title", "article_source"],
    )

    log_message("Data deduplication process finished.")
