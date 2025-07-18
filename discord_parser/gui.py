# Authored by AI: Google's Gemini Model
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from utils.logger_setup import logger
from logic.file_handler import load_csv_file
from logic.data_processor import export_data, filter_dataframe_by_date, BAD_WORDS
from logic.graph_handler import create_frequency_graph
from logic.analytics_handler import get_author_summary, get_datetime_summary, get_content_summary, get_attachment_summary
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os
import threading
import queue

class App(tk.Tk):
    """Main application GUI. v1.6.1"""
    def __init__(self):
        super().__init__()
        logger.info("Initializing GUI.")
        self.title("Discord CSV Parser v1.6.1")
        self.geometry("1150x800")
        self.minsize(1000, 750)

        # State and Data
        self.loaded_data = None; self.filtered_dataframe = None; self.graph_canvas = None
        self.loaded_filepath = None; self.last_export_path = None; self.author_data = []
        self.author_widgets = []; self.last_snipped_words = None

        # Threading
        self.task_queue = queue.Queue()
        self.result_queue = queue.Queue()
        self.worker_thread = threading.Thread(target=self.worker, daemon=True)
        self.worker_thread.start()
        
        # UI Elements
        self.style = ttk.Style(self); self.style.theme_use('vista')
        self.paned_window = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        
        status_frame = ttk.Frame(self)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X, ipady=2)
        self.status_bar = ttk.Label(status_frame, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.progress_bar = ttk.Progressbar(status_frame, orient='horizontal', mode='determinate')
        self.progress_bar.pack(side=tk.RIGHT)
        self.progress_bar.pack_forget()

        self.create_file_pane(); self.create_config_pane(); self.create_preview_pane()
        
        logger.info("GUI initialization complete.")
        self.after(100, self.process_results)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_file_pane(self):
        # This method is unchanged
        file_pane = ttk.Frame(self.paned_window, width=280); file_pane.pack(fill=tk.BOTH, expand=False, side=tk.LEFT); file_pane.pack_propagate(False)
        upload_frame = ttk.LabelFrame(file_pane, text="File Upload"); upload_frame.pack(padx=10, pady=10, fill=tk.X)
        self.filepath_label = ttk.Label(upload_frame, text="No file selected.", wraplength=250); self.filepath_label.pack(padx=5, pady=5)
        self.load_button = ttk.Button(upload_frame, text="Load CSV File", command=self.select_file); self.load_button.pack(padx=5, pady=5, fill=tk.X)
        file_mgmt_frame = ttk.Frame(upload_frame); file_mgmt_frame.pack(fill=tk.X, padx=5, pady=(0,5))
        self.open_file_btn = ttk.Button(file_mgmt_frame, text="Open File", command=self.open_loaded_file, state=tk.DISABLED); self.open_file_btn.pack(side=tk.LEFT, expand=True, fill=tk.X)
        self.open_folder_btn = ttk.Button(file_mgmt_frame, text="Open Folder", command=self.open_loaded_folder, state=tk.DISABLED); self.open_folder_btn.pack(side=tk.LEFT, expand=True, fill=tk.X)
        details_frame = ttk.LabelFrame(file_pane, text="File Details"); details_frame.pack(padx=10, pady=10, fill=tk.X)
        self.details_messages_label = ttk.Label(details_frame, text="Total Messages: -"); self.details_messages_label.pack(padx=5, pady=2, anchor=tk.W)
        self.details_authors_label = ttk.Label(details_frame, text="Total Authors: -"); self.details_authors_label.pack(padx=5, pady=2, anchor=tk.W)
        self.details_words_label = ttk.Label(details_frame, text="Total Words: -"); self.details_words_label.pack(padx=5, pady=2, anchor=tk.W)
        self.details_unique_words_label = ttk.Label(details_frame, text="Unique Words: -"); self.details_unique_words_label.pack(padx=5, pady=2, anchor=tk.W)
        self.details_date_range_label = ttk.Label(details_frame, text="Date Range: -"); self.details_date_range_label.pack(padx=5, pady=2, anchor=tk.W)
        self.details_size_label = ttk.Label(details_frame, text="File Size: -"); self.details_size_label.pack(padx=5, pady=2, anchor=tk.W)
        export_details_frame = ttk.LabelFrame(file_pane, text="Export Details"); export_details_frame.pack(padx=10, pady=10, fill=tk.X)
        ttk.Button(export_details_frame, text="Preview Export Settings", command=self.show_export_settings).pack(fill=tk.X, padx=5, pady=5)
        export_frame = ttk.LabelFrame(file_pane, text="Export"); export_frame.pack(padx=10, pady=10, fill=tk.X, side=tk.BOTTOM)
        self.export_csv_btn = ttk.Button(export_frame, text="Export as CSV", command=lambda: self.trigger_export('csv')); self.export_csv_btn.pack(padx=5, pady=5, fill=tk.X)
        self.export_txt_btn = ttk.Button(export_frame, text="Export as TXT", command=lambda: self.trigger_export('txt')); self.export_txt_btn.pack(padx=5, pady=5, fill=tk.X)
        export_mgmt_frame = ttk.Frame(export_frame); export_mgmt_frame.pack(fill=tk.X, padx=5, pady=(0,5))
        self.open_export_btn = ttk.Button(export_mgmt_frame, text="Open Last Export", command=self.open_exported_file, state=tk.DISABLED); self.open_export_btn.pack(side=tk.LEFT, expand=True, fill=tk.X)
        self.open_export_folder_btn = ttk.Button(export_mgmt_frame, text="Open Folder", command=self.open_exported_folder, state=tk.DISABLED); self.open_export_folder_btn.pack(side=tk.LEFT, expand=True, fill=tk.X)
        ttk.Label(export_frame, text="Last Export:").pack(padx=5, pady=(10, 2), anchor=tk.W)
        self.export_preview_label = ttk.Label(export_frame, text="Size: - | Lines: -"); self.export_preview_label.pack(padx=5, pady=2, anchor=tk.W)
        self.paned_window.add(file_pane, weight=1)

    def create_config_pane(self):
        # This method is unchanged
        config_pane = ttk.Frame(self.paned_window, width=550); config_pane.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        self.notebook = ttk.Notebook(config_pane); self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)
        self.create_authors_tab(self.notebook); self.create_datetime_tab(self.notebook); self.create_content_tab(self.notebook); self.create_attachments_tab(self.notebook)
        self.paned_window.add(config_pane, weight=3)

    def create_preview_pane(self):
        # This method is unchanged
        preview_pane = ttk.Frame(self.paned_window, width=320); preview_pane.pack(fill=tk.BOTH, expand=False, side=tk.RIGHT); preview_pane.pack_propagate(False)
        self.preview_frame = ttk.LabelFrame(preview_pane, text="Analytics Dashboard"); self.preview_frame.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
        self.preview_text = tk.Text(self.preview_frame, state='disabled', wrap='word', background="#f0f0f0", font=("Courier New", 9), borderwidth=0); self.preview_text.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)
        self.paned_window.add(preview_pane, weight=2)

    def create_authors_tab(self, notebook):
        # This method is unchanged
        tab = ttk.Frame(notebook); notebook.add(tab, text="Authors")
        controls_frame = ttk.Frame(tab); controls_frame.pack(fill=tk.X, padx=10, pady=10)
        ttk.Label(controls_frame, text="Sort by:").pack(side=tk.LEFT, padx=(0,5))
        self.author_sort_combo = ttk.Combobox(controls_frame, state="readonly", values=["By Name", "By ID", "By Message Count"]); self.author_sort_combo.pack(side=tk.LEFT)
        self.author_sort_combo.bind("<<ComboboxSelected>>", self.on_author_sort_change)
        ttk.Button(controls_frame, text="Select All", command=lambda: self.select_all_authors(True)).pack(side=tk.RIGHT)
        ttk.Button(controls_frame, text="Deselect All", command=lambda: self.select_all_authors(False)).pack(side=tk.RIGHT, padx=5)
        list_frame = ttk.Frame(tab); list_frame.pack(padx=10, pady=0, fill=tk.BOTH, expand=True)
        self.author_canvas = tk.Canvas(list_frame, borderwidth=0); self.author_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.author_canvas.yview); scrollbar.pack(side=tk.RIGHT, fill="y")
        self.author_scrollable_frame = ttk.Frame(self.author_canvas)
        self.author_canvas.configure(yscrollcommand=scrollbar.set)
        self.author_canvas.create_window((0, 0), window=self.author_scrollable_frame, anchor="nw")
        self.author_scrollable_frame.bind("<Configure>", lambda e: self.author_canvas.configure(scrollregion=self.author_canvas.bbox("all")))
        options_frame = ttk.LabelFrame(tab, text="Formatting Options"); options_frame.pack(padx=10, pady=10, fill=tk.X, side=tk.BOTTOM)
        self.author_format_var = tk.StringVar(value="both"); rad_cmd = self.update_author_options_state
        author_opts = {"Author ID & Name": "both", "Name Only": "name", "ID Only": "id", "Use Custom Nickname": "nickname", "Anonymize": "anonymize", "Omit Author": "omit"}
        for text, val in author_opts.items():
            ttk.Radiobutton(options_frame, text=text, variable=self.author_format_var, value=val, command=rad_cmd).pack(anchor=tk.W, padx=5)
        self.anonymize_key_var = tk.BooleanVar(value=True)
        self.anonymize_key_checkbutton = ttk.Checkbutton(options_frame, text="Create anonymization key file", variable=self.anonymize_key_var, state=tk.DISABLED); self.anonymize_key_checkbutton.pack(anchor=tk.W, padx=20, pady=5)

    def create_datetime_tab(self, notebook):
        # This method is unchanged
        tab = ttk.Frame(notebook); notebook.add(tab, text="Date & Time")
        filter_frame = ttk.LabelFrame(tab, text="Date Range Filter (Format: YYYY-MM-DD)"); filter_frame.pack(padx=10, pady=10, fill=tk.X)
        self.start_date_var = tk.StringVar(); self.end_date_var = tk.StringVar()
        ttk.Label(filter_frame, text="Start:").pack(side=tk.LEFT, padx=5); ttk.Entry(filter_frame, textvariable=self.start_date_var, width=12).pack(side=tk.LEFT)
        ttk.Label(filter_frame, text="End:").pack(side=tk.LEFT, padx=5); ttk.Entry(filter_frame, textvariable=self.end_date_var, width=12).pack(side=tk.LEFT)
        ttk.Button(filter_frame, text="Apply Filter", command=self.apply_date_filter).pack(side=tk.RIGHT, padx=5)
        self.graph_frame = ttk.LabelFrame(tab, text="Message Frequency"); self.graph_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        graph_options_frame = ttk.LabelFrame(tab, text="Graph Scale"); graph_options_frame.pack(padx=10, pady=10, fill=tk.X)
        self.graph_scale_var = tk.StringVar(value="day")
        for scale in ["Hour", "Day", "Week", "Month"]:
            ttk.Radiobutton(graph_options_frame, text=scale, variable=self.graph_scale_var, value=scale.lower(), command=self.start_graph_task).pack(side=tk.LEFT, padx=5)
        
    def create_content_tab(self, notebook):
        # This method is unchanged
        tab = ttk.Frame(notebook); notebook.add(tab, text="Content")
        trim_frame = ttk.LabelFrame(tab, text="Content Trimming"); trim_frame.pack(padx=10, pady=10, fill=tk.X)
        self.trim_logic_var = tk.StringVar(value="AND"); logic_frame = ttk.Frame(trim_frame); logic_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(logic_frame, text="Keep message if it matches:").pack(side=tk.LEFT)
        ttk.Radiobutton(logic_frame, text="ALL conditions (AND)", variable=self.trim_logic_var, value="AND").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(logic_frame, text="ANY condition (OR)", variable=self.trim_logic_var, value="OR").pack(side=tk.LEFT, padx=5)
        self.trim_chars_min_var = tk.StringVar(value="0"); self.trim_chars_max_var = tk.StringVar(value="4000")
        self.trim_words_min_var = tk.StringVar(value="0"); self.trim_words_max_var = tk.StringVar(value="1000")
        self.trim_chars_min_enabled = tk.BooleanVar(); self.trim_chars_max_enabled = tk.BooleanVar()
        self.trim_words_min_enabled = tk.BooleanVar(); self.trim_words_max_enabled = tk.BooleanVar()
        def add_trim_row(parent, text, min_var, max_var, min_enabled_var, max_enabled_var):
            frame = ttk.Frame(parent); frame.pack(fill=tk.X, padx=5, pady=5)
            ttk.Label(frame, text=text, width=12).pack(side=tk.LEFT)
            min_check = ttk.Checkbutton(frame, text="Min:", variable=min_enabled_var); min_check.pack(side=tk.LEFT)
            min_entry = ttk.Entry(frame, textvariable=min_var, width=7); min_entry.pack(side=tk.LEFT)
            max_check = ttk.Checkbutton(frame, text="Max:", variable=max_enabled_var); max_check.pack(side=tk.LEFT, padx=(10,0))
            max_entry = ttk.Entry(frame, textvariable=max_var, width=7); max_entry.pack(side=tk.LEFT)
        add_trim_row(trim_frame, "Characters:", self.trim_chars_min_var, self.trim_chars_max_var, self.trim_chars_min_enabled, self.trim_chars_max_enabled)
        add_trim_row(trim_frame, "Words:", self.trim_words_min_var, self.trim_words_max_var, self.trim_words_min_enabled, self.trim_words_max_enabled)
        filter_frame = ttk.LabelFrame(tab, text="Content Filtering"); filter_frame.pack(padx=10, pady=10, fill=tk.X)
        self.bad_word_filter_var = tk.BooleanVar(value=False)
        bad_word_check = ttk.Checkbutton(filter_frame, text="<Snip> words from bad_words.txt", variable=self.bad_word_filter_var); bad_word_check.pack(anchor=tk.W, padx=5)
        if not BAD_WORDS: bad_word_check.config(state=tk.DISABLED)

    def create_attachments_tab(self, notebook):
        # This method is unchanged
        tab = ttk.Frame(notebook); notebook.add(tab, text="Attachments & Reactions")
        include_frame = ttk.LabelFrame(tab, text="Inclusion"); include_frame.pack(padx=10, pady=10, fill=tk.X)
        self.include_attachments_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(include_frame, text="Include Attachments", variable=self.include_attachments_var).pack(anchor=tk.W, padx=5)
        self.include_reactions_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(include_frame, text="Include Reactions", variable=self.include_reactions_var).pack(anchor=tk.W, padx=5)
        attach_format_frame = ttk.LabelFrame(tab, text="Attachment Formatting"); attach_format_frame.pack(padx=10, pady=10, fill=tk.X)
        self.attach_format_var = tk.StringVar(value="link")
        ttk.Radiobutton(attach_format_frame, text="Full Link", variable=self.attach_format_var, value="link").pack(anchor=tk.W, padx=5)
        ttk.Radiobutton(attach_format_frame, text="<attachment> tag", variable=self.attach_format_var, value="tag").pack(anchor=tk.W, padx=5)
        ttk.Radiobutton(attach_format_frame, text="Filename only", variable=self.attach_format_var, value="filename").pack(anchor=tk.W, padx=5)

    def worker(self):
        while True:
            try:
                task = self.task_queue.get()
                if task is None: break
                task_name, func, args, kwargs = task
                
                # Conditionally add the progress callback only for 'export' tasks
                if task_name == 'export':
                    def progress_callback(percentage, message):
                        self.result_queue.put(('progress', (percentage, message)))
                    kwargs['progress_callback'] = progress_callback
                
                result = func(*args, **kwargs)
                self.result_queue.put((task_name, result))
            except Exception as e:
                self.result_queue.put(('error', e))

    def process_results(self):
        # This method is unchanged
        try:
            while not self.result_queue.empty():
                task_name, result = self.result_queue.get_nowait()
                if task_name == 'progress':
                    percentage, message = result
                    self.status_bar.config(text=message)
                    self.progress_bar['value'] = percentage
                elif task_name == 'load_file':
                    self.set_ui_busy(False)
                    if result: self.update_gui_with_file_data(result)
                    else: messagebox.showerror("File Load Error", "Could not load the file. Check console for details.")
                elif task_name == 'graph':
                    if self.graph_canvas: self.graph_canvas.get_tk_widget().destroy()
                    if result:
                        self.graph_canvas = FigureCanvasTkAgg(result, master=self.graph_frame); self.graph_canvas.draw(); self.graph_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
                elif task_name == 'analytics':
                    self.preview_text.config(state='normal'); self.preview_text.delete('1.0', tk.END); self.preview_text.insert('1.0', result); self.preview_text.config(state='disabled')
                elif task_name == 'export':
                    self.set_ui_busy(False)
                    if result and result.get("success"):
                        self.last_export_path = result['save_path']; self.last_snipped_words = result['snipped_words']
                        self.open_export_btn.config(state=tk.NORMAL); self.open_export_folder_btn.config(state=tk.NORMAL)
                        self.export_preview_label.config(text=f"Size: {result['final_size']} | Lines: {result['line_count']}")
                        messagebox.showinfo("Export Successful", f"File successfully saved to:\n{result['save_path']}")
                        self.start_analytics_task()
                    else:
                        messagebox.showerror("Export Failed", f"Failed to export the file. Check the console log for details.\n\nError: {result.get('error', 'Unknown')}")
                elif task_name == 'error':
                    self.set_ui_busy(False)
                    logger.critical(f"Unhandled exception in worker thread: {result}", exc_info=True)
                    messagebox.showerror("Worker Thread Error", f"An unexpected error occurred in a background task:\n\n{result}")
        finally:
            self.after(100, self.process_results)

    def set_ui_busy(self, is_busy):
        # This