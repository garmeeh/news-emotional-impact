import pandas as pd  # type: ignore
import os
from datetime import datetime

# Define constants
BASE_DIR = "exported_datasets"
LOG_FILE = "create_random_samples_log.txt"
NUM_SAMPLE_ROWS = 100


SENTIMENTS_FILE = os.path.join(BASE_DIR, "news_article_sentiments_dataset_final.csv")
ARTICLES_FILE = os.path.join(BASE_DIR, "news_articles_dataset_final.csv")


RANDOM_SENTIMENTS_FILE = os.path.join(
    BASE_DIR, "random_sample_news_article_sentiments.csv"
)
RANDOM_ARTICLES_FILE = os.path.join(BASE_DIR, "random_sample_news_articles.csv")


def log_message(message: str) -> None:
    """Appends a message to the log file and prints it."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{now}] {message}"
    print(log_entry)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_entry + "\\n")


def create_random_sample(
    input_file_path: str, output_file_path: str, num_rows: int = NUM_SAMPLE_ROWS
) -> None:
    """
    Reads a CSV file, creates a random sample of rows, and saves it to a new CSV file.

    Args:
        input_file_path (str): Path to the input CSV file.
        output_file_path (str): Path to save the sampled CSV file.
        num_rows (int): The number of rows to sample. If the original file has
                        fewer rows, all rows are taken.
    """
    log_message(
        f"Processing {input_file_path} to create random sample at {output_file_path}..."
    )

    if not os.path.exists(input_file_path):
        log_message(f"  ERROR: Input file {input_file_path} not found. Skipping.")
        return

    try:
        os.makedirs(os.path.dirname(output_file_path), exist_ok=True)

        df = pd.read_csv(input_file_path, low_memory=False)
        log_message(f"  Successfully read {input_file_path}. It has {len(df)} rows.")

        if df.empty:
            log_message(
                f"  Input file {input_file_path} is empty (or contains only headers). "
                f"Writing an empty file (with headers if present) to {output_file_path}."
            )
            # This writes an empty df with headers if df.columns is populated from an empty (but headered) CSV
            df.to_csv(output_file_path, index=False)
            return

        if len(df) <= num_rows:
            sampled_df = df.copy()
            log_message(
                f"  Taking all {len(sampled_df)} rows from {input_file_path} "
                f"as it has {len(df)} <= {num_rows} rows."
            )
        else:
            sampled_df = df.sample(
                n=num_rows, random_state=42
            )  # random_state for reproducibility
            log_message(f"  Sampled {len(sampled_df)} rows from {input_file_path}.")

        sampled_df.to_csv(output_file_path, index=False)
        log_message(f"  Successfully wrote random sample to {output_file_path}.")

    except pd.errors.EmptyDataError:
        log_message(
            f"  INFO: Input file {input_file_path} is empty (no data, possibly no headers). "
            f"Creating an empty output file {output_file_path}."
        )
        with open(output_file_path, "w", encoding="utf-8"):
            pass
    except Exception as e:
        log_message(
            f"  ERROR: An unexpected error occurred while processing {input_file_path}: {e}"
        )


if __name__ == "__main__":
    # Clear previous log file
    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)
    log_message("Starting script to create random samples from cleaned data.")

    os.makedirs(BASE_DIR, exist_ok=True)

    # Process cleaned sentiments file
    create_random_sample(
        input_file_path=SENTIMENTS_FILE,
        output_file_path=RANDOM_SENTIMENTS_FILE,
        num_rows=NUM_SAMPLE_ROWS,
    )

    # Process cleaned articles file
    create_random_sample(
        input_file_path=ARTICLES_FILE,
        output_file_path=RANDOM_ARTICLES_FILE,
        num_rows=NUM_SAMPLE_ROWS,
    )

    log_message("Finished creating random samples.")
