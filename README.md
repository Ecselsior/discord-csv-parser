!!! THIS PROJECT IS GENERATED WITH AI !!!
<img width="1004" height="1107" alt="image" src="https://github.com/user-attachments/assets/ed576b8f-83dc-4f80-bbd9-6add159f208a" />

Discord CSV Parser

A desktop application built with Python and Tkinter for parsing, analyzing, and exporting data from Discord CSV message exports. This tool helps users gain insights into their Discord conversations, filter messages, and visualize activity over time.

Features

* CSV File Loading & Analysis:
  * Loads Discord message CSV files.
  * Provides detailed statistics: total messages, unique authors, total words, unique words, file size, and date range.
* Data Filtering:
  * Author Filtering: Select specific authors to include or exclude.
  * Date & Time Filtering: Filter messages by a custom date range.
  * Content Trimming: Filter messages by character and word count (min/max).
  * Bad Word Snipping: Censor or "snip" specified bad words from message content (uses a configurable list).
* Analytics & Visualization:
  * Generates interactive message frequency graphs (hourly, daily, weekly, monthly) using Matplotlib.
  * Displays summary analytics for authors, date/time, content, and attachments/reactions.
* Export Options:
  * Export filtered data to new CSV or TXT files.
  * Option to compress the exported output into a .zip file.
* User-Friendly GUI:
  * Intuitive Tkinter-based graphical user interface.
  * Real-time status updates and progress bar for long-running tasks.
  * Background threading to keep the UI responsive during data processing.

Prerequisites

Before running this application, ensure you have:

* Python 3.x (Python 3.13 is recommended as per setup.bat).
* Discord Message Export CSV: You'll need a CSV file exported from Discord containing your message history. This application expects columns like AuthorID, Author, Date, and Content.

Setup and Installation

Follow these steps to get the application running on your Windows machine:

1. Clone the repository:
   git clone [https://github.com/Ecselsior/discord-csv-parser.git](https://github.com/Ecselsior/discord-csv-parser.git)
   cd discord-csv-parser

2. Run the setup script:
   The setup.bat script will create a Python virtual environment and install all necessary dependencies.
   setup.bat

   * Note: If you encounter issues, ensure Python 3.x is correctly installed and added to your system's PATH.

3. Launch the application:
   Once setup is complete, use the launch.bat script to start the GUI.
   launch.bat

Usage

1. Load CSV File:
   * Click the "Load CSV File" button in the "File Upload" section.
   * Select your Discord message export CSV file.
   * The application will display file details and basic analytics.

2. Configure Filters and Options (Tabs):
   * Authors Tab: Select which authors' messages to include and how their names should be formatted in the output (e.g., anonymize, use nicknames).
   * Date & Time Tab: Apply a date range filter and view a message frequency graph.
   * Content Tab: Set minimum/maximum character/word counts for messages, and enable the "snip bad words" feature.
   * Attachments & Reactions Tab: Choose whether to include attachments and reactions in the output, and how attachment links are formatted.

3. Export Data:
   * After applying filters and settings, click "Export as CSV" or "Export as TXT".
   * Choose a save location and filename.
   * Optionally, check "Compress output to a .zip file" to save the exported file as a zip archive.

License

This project is licensed under the MIT License - see the LICENSE file for details (if applicable, otherwise state "No specific license applied yet").
