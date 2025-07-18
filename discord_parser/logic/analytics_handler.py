# Authored by AI: Google's Gemini Model
from utils.logger_setup import logger
import pandas as pd
from collections import Counter
from logic.data_processor import _format_content, _scrub_author_from_content

def _header(title):
    return f"{title.upper()}\n" + "=" * 35 + "\n"

def get_author_summary(df, author_data, settings):
    if df is None or df.empty: return "No data to analyze."
    selected_ids = settings.get('selected_author_ids', [])
    selected_author_data = [a for a in author_data if a['id'] in selected_ids]
    
    scrubbed_chars = 0
    if settings.get('scrub_author_from_content'):
        for row in df.itertuples():
            if row.AuthorID in selected_ids:
                original_len = len(row.Content) if isinstance(row.Content, str) else 0
                scrubbed_content = _scrub_author_from_content(row.Content, row.Author, row.AuthorID, settings)
                scrubbed_chars += original_len - len(scrubbed_content)

    filtered_df = df[df['AuthorID'].isin(selected_ids)]
    total_messages = len(filtered_df)
    
    summary = _header(f"Author Analytics ({len(selected_ids)}/{len(author_data)} Selected)")
    summary += f"Messages from selection: {total_messages:,}\n"
    if scrubbed_chars > 0:
        summary += f"Characters scrubbed from content: {scrubbed_chars:,}\n"
    summary += "\nTop 5 Selected Authors by Message Count:\n"
    sorted_authors = sorted(selected_author_data, key=lambda x: x['count'], reverse=True)
    for i, author in enumerate(sorted_authors[:5]):
        percentage = (author['count'] / total_messages) * 100 if total_messages > 0 else 0
        summary += f"  {i+1}. {author['name']} ({author['count']:,}, {percentage:.1f}%)\n"
    return summary

def get_datetime_summary(df):
    if df is None or df.empty: return "No data to analyze."
    summary = _header(f"Date & Time Summary ({len(df):,} Messages)")
    day_counts = df['Date'].dt.day_name().value_counts()
    summary += "Messages by Day of the Week:\n"
    for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]:
        summary += f"  - {day:<9}: {day_counts.get(day, 0):,}\n"
    summary += "\nMessages by Hour of the Day (UTC):\n"
    hour_counts = df['Date'].dt.hour.value_counts().sort_index()
    for hour, count in hour_counts.items():
        summary += f"  - Hour {hour:02d}: {count:,}\n"
    return summary

def get_content_summary(df, settings):
    if df is None or df.empty: return "No data to analyze."
    
    original_chars, processed_chars, removed_messages = 0, 0, 0
    snipped_words_counter = Counter()
    
    for row in df.itertuples():
        original_len = len(row.Content) if isinstance(row.Content, str) else 0
        original_chars += original_len
        processed = _format_content(row.Content, row.Author, row.AuthorID, settings, snipped_words_counter)
        if processed is None: removed_messages += 1
        else: processed_chars += len(processed)

    total_messages = len(df)
    summary = _header(f"Content Analytics Dry Run")
    summary += f"Messages that would be REMOVED by trimming: {removed_messages:,}\n"
    summary += f"Characters SAVED/REMOVED by all operations: {original_chars - processed_chars:,}\n\n"
    
    if snipped_words_counter:
        summary += f"Total words that would be SNIPPED: {sum(snipped_words_counter.values()):,}\n"
        summary += "Top 5 Snipped Words (from bad_words.txt):\n"
        for i, (word, count) in enumerate(snipped_words_counter.most_common(5)):
            summary += f"  {i+1}. '{word}' ({count:,} times)\n"
    return summary
    
def get_attachment_summary(df, settings):
    if df is None or df.empty: return "No data to analyze."
    summary = _header(f"Attachment/Reaction Analytics")
    
    if 'Attachments' in df.columns:
        if not settings.get('include_attachments'):
            summary += f"Attachments will be excluded ({df['Attachments'].count():,} msgs affected).\n"
        else:
            summary += f"Messages with attachments: {df['Attachments'].count():,}\n"
    
    if 'Reactions' in df.columns:
        if not settings.get('include_reactions'):
            summary += f"Reactions will be excluded ({df['Reactions'].count():,} msgs affected).\n"
        else:
            summary += f"Messages with reactions: {df['Reactions'].count():,}\n"
    return summary