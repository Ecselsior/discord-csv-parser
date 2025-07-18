# Authored by AI: Google's Gemini Model
from utils.logger_setup import logger
import os
import pandas as pd
import re

def load_csv_file(filepath):
    """
    Loads and performs detailed analysis of a CSV file.
    Returns a dictionary of file metadata or None on failure.
    """
    logger.info(f"Begin loading and detailed analysis of file: {filepath}")
    if not filepath or not os.path.exists(filepath):
        logger.error(f"File path is invalid or does not exist: {filepath}")
        return None
    
    try:
        df = pd.read_csv(filepath, on_bad_lines='warn')
        logger.info("CSV file read into DataFrame successfully.")

        required_columns = ['AuthorID', 'Author', 'Date', 'Content']
        if not all(col in df.columns for col in required_columns):
            logger.error(f"CSV is missing one of the required columns: {required_columns}")
            return None

        # --- Perform Analysis ---
        df['Content'] = df['Content'].astype(str)
        df['Date'] = pd.to_datetime(df['Date'])
        
        file_size = os.path.getsize(filepath)
        total_messages = len(df)
        
        # Word counts (can be slow on very large files)
        all_words = df['Content'].str.cat(sep=' ').split()
        total_words = len(all_words)
        unique_words = len(set(word.lower() for word in all_words))

        first_date = df['Date'].min()
        last_date = df['Date'].max()
        date_range_days = (last_date - first_date).days

        # Author analysis
        author_msg_counts = df['AuthorID'].value_counts().to_dict()
        unique_authors_df = df[['AuthorID', 'Author']].drop_duplicates(subset=['AuthorID']).dropna()
        
        author_data = [
            {
                "id": row['AuthorID'],
                "name": row['Author'],
                "count": author_msg_counts.get(row['AuthorID'], 0)
            }
            for index, row in unique_authors_df.iterrows()
        ]
        total_authors = len(author_data)

        logger.info("Detailed file analysis complete.")
        return {
            "filepath": filepath,
            "dataframe": df,
            "size": f"{file_size / 1024:.2f} KB",
            "total_messages": f"{total_messages:,}",
            "total_authors": f"{total_authors:,}",
            "total_words": f"{total_words:,}",
            "unique_words": f"{unique_words:,}",
            "first_date": first_date.strftime('%Y-%m-%d %H:%M:%S'),
            "last_date": last_date.strftime('%Y-%m-%d %H:%M:%S'),
            "date_range_days": f"{date_range_days} days",
            "authors": author_data,
        }
    except Exception as e:
        logger.critical(f"An unexpected error occurred while processing {filepath}: {e}", exc_info=True)
        return None