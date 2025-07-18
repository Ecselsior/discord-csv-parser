# Authored by AI: Google's Gemini Model
from utils.logger_setup import logger
import pandas as pd
from matplotlib.figure import Figure
from matplotlib.ticker import MaxNLocator

def create_frequency_graph(df, scale):
    """Generates a message frequency graph from the DataFrame."""
    logger.info(f"Generating message frequency graph with scale: {scale}")
    if df is None or df.empty:
        logger.warning("DataFrame is empty, cannot generate graph."); return None

    try:
        fig = Figure(figsize=(5, 4), dpi=100)
        ax = fig.add_subplot(111)

        temp_df = df.set_index('Date')
        
        freq_map = {'hour': 'h', 'day': 'D', 'week': 'W-MON', 'month': 'ME'}
        freq_code = freq_map.get(scale.lower(), 'D')
        
        message_counts = temp_df.resample(freq_code).size()

        # Plot with numerical index first
        ax.bar(range(len(message_counts)), message_counts.values, color='skyblue')

        # Generate and set custom labels
        date_format = '%Y-%m-%d'
        if scale == 'month': date_format = '%Y-%m'
        elif scale == 'hour': date_format = '%Y-%m-%d %H:%M'
        
        labels = [d.strftime(date_format) for d in message_counts.index]
        ax.set_xticks(range(len(message_counts)))
        ax.set_xticklabels(labels)
        
        ax.set_title(f'Messages per {scale.capitalize()}', fontsize=10)
        ax.set_xlabel('Time Period', fontsize=8)
        ax.set_ylabel('Number of Messages', fontsize=8)
        
        ax.xaxis.set_major_locator(MaxNLocator(nbins=10, integer=True))
        fig.autofmt_xdate(rotation=45, ha='right')
        ax.tick_params(axis='x', labelsize=7)
        ax.tick_params(axis='y', labelsize=8)
        fig.tight_layout()
        
        logger.info("Graph generation successful.")
        return fig
    except Exception as e:
        logger.error(f"Failed to generate graph: {e}", exc_info=True); return None