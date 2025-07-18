# Authored by AI: Google's Gemini Model
from utils.logger_setup import logger
import pandas as pd
import os
import re
from collections import Counter
from utils.timing import Timer
import requests
from bs4 import BeautifulSoup

BAD_WORDS_PATTERN = None
try:
    with open(os.path.join(os.path.dirname(__file__), '..', 'bad_words.txt'), 'r') as f:
        bad_words = [line.strip().lower() for line in f if line.strip()]
    if bad_words:
        pattern = r'\b(' + '|'.join(re.escape(word) for word in bad_words) + r')\b'
        BAD_WORDS_PATTERN = re.compile(pattern, re.IGNORECASE)
        logger.info(f"Loaded and compiled {len(bad_words)} words from bad_words.txt filter.")
except FileNotFoundError:
    logger.warning("bad_words.txt not found. Bad word filter will not be available.")
except Exception as e:
    logger.error(f"Error loading bad_words.txt: {e}")

def filter_dataframe_by_date(df, start_date_str, end_date_str):
    with Timer(f"Filtering date range ('{start_date_str}' to '{end_date_str}')"):
        try:
            start_date = pd.to_datetime(start_date_str); end_date = pd.to_datetime(end_date_str).replace(hour=23, minute=59, second=59)
            if not pd.api.types.is_datetime64_any_dtype(df['Date']): df['Date'] = pd.to_datetime(df['Date'])
            mask = (df['Date'] >= start_date) & (df['Date'] <= end_date)
            return df.loc[mask]
        except Exception as e:
            logger.error(f"Error during date filtering: {e}", exc_info=True); return df

def _fetch_url_title(url):
    try:
        response = requests.get(url, timeout=3, headers={'User-Agent': 'Mozilla/5.0'}); response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.title.string.strip() if soup.title else None
        return title.replace('\n', ' ').replace('\r', ' ')
    except requests.RequestException: return None

def _scrub_author_from_content(content, author_name, author_id, settings):
    """Dynamically scrubs author identifiers from the start of content."""
    author_format = settings.get('author_format')
    to_remove = []
    if author_format == 'id_only': to_remove.append(str(author_name))
    elif author_format == 'name_only' or author_format == 'nickname': to_remove.append(str(author_id))
    elif author_format in ['numeric_keys', 'anonymize']: to_remove.extend([str(author_name), str(author_id)])

    for item in to_remove:
        if item and content.startswith(f"{item}: "):
            content = content[len(item) + 2:]
    return content

def _format_content(content, author_name, author_id, settings, snipped_words_counter):
    if not isinstance(content, str) or content.lower() == 'nan': return None
    
    if settings.get('scrub_author_from_content'):
        content = _scrub_author_from_content(content, author_name, author_id, settings)

    def format_tag(tag_name): return f"{tag_name}" if settings.get('omit_brackets') else f"<{tag_name}>"
    if settings.get('shorten_urls', False):
        url_pattern = re.compile(r'https?://[^\s<>"]+|www\.[^\s<>"]+')
        url_format = settings.get('url_format_mode', 'tag_generic')
        if url_format == 'blank': content = url_pattern.sub('', content)
        else:
            urls = url_pattern.findall(content)
            for url in urls:
                if url_format == 'tag_domain':
                    try: replacement = format_tag(url.split('//')[-1].split('/')[0])
                    except: replacement = format_tag('link')
                else:
                    if 'youtube.com' in url or 'youtu.be' in url: replacement = format_tag('youtube')
                    else: replacement = format_tag('link')
                content = content.replace(url, replacement, 1)

    filter_mode = settings.get('bad_word_filter_mode', 'disabled')
    if filter_mode != 'disabled' and BAD_WORDS_PATTERN:
        matches = list(BAD_WORDS_PATTERN.finditer(content))
        if matches:
            if filter_mode == 'snip_message': return format_tag("message removed")
            elif filter_mode == 'snip_word':
                for match in matches: snipped_words_counter[match.group(0).lower()] += 1
                replacement_text = settings.get('snip_replacement', format_tag('snip'))
                content = BAD_WORDS_PATTERN.sub(replacement_text, content)

    if settings.get('normalize_whitespace', False): content = re.sub(r'\s+', ' ', content).strip()
    keep = True; char_len = len(content); word_count = len(content.split())
    if settings['trim_logic'] == 'AND':
        if settings['trim_chars_min_enabled'] and char_len < settings['trim_chars_min']: keep = False
        if settings['trim_chars_max_enabled'] and char_len > settings['trim_chars_max']: keep = False
        if settings['trim_words_min_enabled'] and word_count < settings['trim_words_min']: keep = False
        if settings['trim_words_max_enabled'] and word_count > settings['trim_words_max']: keep = False
    elif settings['trim_logic'] == 'OR':
        conditions = []
        if settings['trim_chars_min_enabled']: conditions.append(char_len >= settings['trim_chars_min'])
        if settings['trim_chars_max_enabled']: conditions.append(char_len <= settings['trim_chars_max'])
        if settings['trim_words_min_enabled']: conditions.append(word_count >= settings['trim_words_min'])
        if settings['trim_words_max_enabled']: conditions.append(word_count <= settings['trim_words_max'])
        if conditions and not any(conditions): keep = False
    if not keep: return None
    return content

def export_data(df, settings, export_format, save_path, progress_callback):
    try:
        with Timer("Total export process"):
            progress_callback(5, "Preparing data..."); processed_df = df.copy(); processed_df.fillna('', inplace=True)
            if settings.get('selected_author_ids'):
                with Timer("Author filtering"): processed_df = processed_df[processed_df['AuthorID'].isin(settings['selected_author_ids'])]
            snipped_words_counter = Counter()
            with Timer("Content processing"):
                total_rows = len(processed_df); processed_content = []
                start_percent, end_percent = 15, 60
                for i, row in enumerate(processed_df.itertuples()):
                    processed_content.append(_format_content(row.Content, row.Author, row.AuthorID, settings, snipped_words_counter))
                    if i % 250 == 0 or i == total_rows - 1:
                        progress = start_percent + ((i + 1) / total_rows) * (end_percent - start_percent)
                        progress_callback(int(progress), f"Processing message content ({i+1}/{total_rows})...")
                processed_df['Content'] = processed_content
                processed_df.dropna(subset=['Content'], inplace=True, ignore_index=True)
            with Timer("Column formatting"):
                progress_callback(75, "Formatting columns...")
                def create_key_file(mapping):
                    key_path = os.path.join(os.path.dirname(save_path), 'export_key.txt')
                    original_authors = df.drop_duplicates(subset=['AuthorID']).set_index('AuthorID')['Author']
                    with open(key_path, 'w', encoding='utf-8') as f:
                        f.write("Export Key\n===================\n")
                        for uid, new_id in mapping.items(): f.write(f"{new_id}: {original_authors.get(uid, 'N/A')} ({uid})\n")
                author_cols_to_process = [col for col in ['AuthorID', 'Author'] if col in processed_df.columns]
                if settings['author_format'] == 'nickname' and settings.get('nicknames'): processed_df['Author'] = processed_df['AuthorID'].map(settings['nicknames'])
                elif settings['author_format'] == 'anonymize' or settings['author_format'] == 'numeric_keys':
                    unique_ids = processed_df['AuthorID'].unique()
                    if settings['author_format'] == 'anonymize': mapping = {uid: f"User{i+1}" for i, uid in enumerate(unique_ids)}
                    else: mapping = {uid: i+1 for i, uid in enumerate(unique_ids)}
                    if settings['create_key_file']: create_key_file(mapping)
                    new_col_name = 'Author' if settings['author_format'] == 'anonymize' else 'AuthorKey'
                    processed_df[new_col_name] = processed_df['AuthorID'].map(mapping)
                    processed_df = processed_df.drop(columns=author_cols_to_process)
                if settings['author_format'] not in ['both', 'nickname', 'numeric_keys', 'anonymize']:
                    if 'AuthorID' in processed_df.columns and settings['author_format'] in ['name', 'omit']: processed_df = processed_df.drop(columns=['AuthorID'])
                    if 'Author' in processed_df.columns and settings['author_format'] in ['id', 'omit']: processed_df = processed_df.drop(columns=['Author'])
                if 'Date' in processed_df.columns:
                    if settings['date_format'] == 'hide': processed_df = processed_df.drop(columns=['Date'])
                    elif settings['date_format'] == 'relative_first': processed_df['Date'] = (processed_df['Date'] - settings['first_date_timestamp']).dt.total_seconds().astype(int)
                    elif settings['date_format'] == 'relative_last': processed_df['Date'] = (settings['last_date_timestamp'] - processed_df['Date']).dt.total_seconds().astype(int)
                    elif settings['date_format'] == 'unix': processed_df['Date'] = (processed_df['Date'] - pd.Timestamp("1970-01-01")) // pd.Timedelta('1s')
                if 'Attachments' in processed_df.columns:
                    if not settings['include_attachments']: processed_df = processed_df.drop(columns=['Attachments'])
                    elif settings['attachment_format'] == 'binary': processed_df['Attachments'] = processed_df['Attachments'].apply(lambda x: '1' if x else '')
                    else:
                        tag = 'att.' if settings.get('omit_brackets') else '<att.>'
                        if settings['attachment_format'] == 'tag': processed_df['Attachments'] = processed_df['Attachments'].apply(lambda x: tag if x else '')
                        elif settings['attachment_format'] == 'filename': processed_df['Attachments'] = processed_df['Attachments'].apply(lambda x: os.path.basename(x.split('?')[0]) if x else '')
                if 'Reactions' in processed_df.columns and not settings['include_reactions']: processed_df = processed_df.drop(columns=['Reactions'])
            if settings.get('group_consecutive'):
                with Timer("Grouping consecutive messages"):
                    progress_callback(85, "Grouping consecutive messages...")
                    group_id_col = 'AuthorID'
                    if 'AuthorID' not in processed_df.columns and 'AuthorKey' in processed_df.columns: group_id_col = 'AuthorKey'
                    if group_id_col in processed_df.columns:
                        author_cols_to_group = [col for col in ['Author', 'AuthorID', 'AuthorKey'] if col in processed_df.columns]
                        for col in author_cols_to_group:
                            if processed_df[col].dtype != 'object': processed_df[col] = processed_df[col].astype('object')
                        mask = processed_df[group_id_col].notna() & (processed_df[group_id_col] == processed_df[group_id_col].shift())
                        processed_df.loc[mask, author_cols_to_group] = ''
            with Timer(f"Writing {export_format.upper()} file"):
                progress_callback(90, f"Writing {export_format.upper()} file...")
                if export_format == 'csv': processed_df.to_csv(save_path, index=False, encoding='utf-8-sig', na_rep='')
                elif export_format == 'txt':
                    with open(save_path, 'w', encoding='utf-8') as f: f.write(processed_df.to_string(index=False, na_rep=''))
            progress_callback(100, "Export complete.")
        return {"success": True, "final_size": f"{os.path.getsize(save_path) / 1024:.2f} KB", "line_count": f"{len(processed_df.index):,}", "snipped_words": snipped_words_counter, "save_path": save_path}
    except Exception as e:
        logger.critical(f"Failed during export process: {e}", exc_info=True); return {"success": False, "error": str(e)}