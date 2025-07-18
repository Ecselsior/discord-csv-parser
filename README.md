!!! THIS PROJECT IS GENERATED WITH AI !!!

Discord CSV Parser
A desktop application built with Python and Tkinter for parsing, analyzing, and exporting data from Discord CSV message exports. This tool helps users gain insights into their Discord conversations, filter messages, and visualize activity over time.

Table of Contents
Features

Prerequisites

Setup and Installation

Usage

Project Structure

Contributing

License

Features
CSV File Loading & Analysis:

Loads Discord message CSV files.

Provides detailed statistics: total messages, unique authors, total words, unique words, file size, and date range.

Data Filtering:

Author Filtering: Select specific authors to include or exclude.

Date & Time Filtering: Filter messages by a custom date range.

Content Trimming: Filter messages by character and word count (min/max).

Bad Word Snipping: Censor or "snip" specified bad words from message content (uses a configurable list).

Analytics & Visualization:

Generates interactive message frequency graphs (hourly, daily, weekly, monthly) using Matplotlib.

Displays summary analytics for authors, date/time, content, and attachments/reactions.

Export Options:

Export filtered data to new CSV or TXT files.

Option to compress the exported output into a .zip file.

User-Friendly GUI:

Intuitive Tkinter-based graphical user interface.

Real-time status updates and progress bar for long-running tasks.

Background threading to keep the UI responsive during data processing.

Prerequisites
Before running this application, ensure you have:

Python 3.x (Python 3.13 is recommended as per setup.bat).

Discord Message Export CSV: You'll need a CSV file exported from Discord containing your message history. This application expects columns like AuthorID, Author, Date, and Content.

Setup and Installation
Follow these steps to get the application running on your Windows machine:

Clone the repository:

git clone https://github.com/Ecselsior/discord-csv-parser.git
cd discord-csv-parser

Run the setup script:
The setup.bat script will create a Python virtual environment and install all necessary dependencies.

setup.bat

Note: If you encounter issues, ensure Python 3.x is correctly installed and added to your system's PATH.

Launch the application:
Once setup is complete, use the launch.bat script to start the GUI.

launch.bat

Usage
Load CSV File:

Click the "Load CSV File" button in the "File Upload" section.

Select your Discord message export CSV file.

The application will display file details and basic analytics.

Configure Filters and Options (Tabs):

Authors Tab: Select which authors' messages to include and how their names should be formatted in the output (e.g., anonymize, use nicknames).

Date & Time Tab: Apply a date range filter and view a message frequency graph.

Content Tab: Set minimum/maximum character/word counts for messages, and enable the "snip bad words" feature.

Attachments & Reactions Tab: Choose whether to include attachments and reactions in the output, and how attachment links are formatted.

Export Data:

After applying filters and settings, click "Export as CSV" or "Export as TXT".

Choose a save location and filename.

Optionally, check "Compress output to a .zip file" to save the exported file as a zip archive.

View Analytics:

The "Analytics Dashboard" on the right will update with summaries based on your loaded and filtered data.

The "Message Frequency" graph in the "Date & Time" tab will visualize message activity.

Project Structure
discord_parser/
├── .gitignore
├── launch.bat             # Script to activate venv and run the app
├── setup.bat              # Script to setup venv and install dependencies
├── .venv/                 # Python Virtual Environment (ignored by Git)
├── discord_parser/
│   ├── bad_words.txt      # Default list for content snipping
│   ├── gui.py             # Main GUI application logic (older version, now main_window.py)
│   ├── main.py            # Entry point for the application
│   ├── lists/             # Directory for various bad word lists
│   │   ├── bad_words.txt
│   │   ├── bad_words_least.txt
│   │   ├── bad_words_mild.txt
│   │   ├── bad_words_moderate.txt
│   │   └── bad_words_severe.txt
│   ├── logic/
│   │   ├── analytics_handler.py # Handles data summarization for analytics
│   │   ├── data_processor.py    # Core logic for data filtering and export
│   │   ├── file_handler.py      # Handles CSV loading and initial data analysis
│   │   └── graph_handler.py     # Generates matplotlib graphs
│   ├── ui/
│   │   ├── config_tabs.py       # Manages the various configuration tabs (Authors, Date, Content, Attachments)
│   │   ├── file_pane.py         # Handles file loading, details display, and export controls
│   │   ├── main_window.py       # The main application window and overall UI orchestration
│   │   └── preview_pane.py      # Displays analytics summaries
│   └── utils/
│       ├── logger_setup.py      # Configures application logging
│       └── timing.py            # Utility for timing operations
└── discord_parser_bundle/ # Potentially for bundled executables (not part of source control)

Contributing
Contributions are welcome! If you have suggestions for improvements, new features, or bug fixes, please feel free to:

Fork the repository.

Create a new branch (git checkout -b feature/your-feature-name).

Make your changes.

Commit your changes (git commit -m 'Add new feature').

Push to the branch (git push origin feature/your-feature-name).

Open a Pull Request.

License
This project is licensed under the MIT License - see the LICENSE file for details (if applicable, otherwise state "No specific license applied yet").
