# Authored by AI: Google's Gemini Model
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os

class FilePane(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, width=280)
        self.pack(fill=tk.BOTH, expand=False, side=tk.LEFT)
        self.pack_propagate(False)
        self.controller = controller

        self.last_export_path = None
        
        upload_frame = ttk.LabelFrame(self, text="File Upload"); upload_frame.pack(padx=10, pady=10, fill=tk.X)
        self.filepath_label = ttk.Label(upload_frame, text="No file selected.", wraplength=250); self.filepath_label.pack(padx=5, pady=5)
        self.load_button = ttk.Button(upload_frame, text="Load CSV File", command=self.select_file); self.load_button.pack(padx=5, pady=5, fill=tk.X)
        file_mgmt_frame = ttk.Frame(upload_frame); file_mgmt_frame.pack(fill=tk.X, padx=5, pady=(0,5))
        self.open_file_btn = ttk.Button(file_mgmt_frame, text="Open File", command=self.open_loaded_file, state=tk.DISABLED); self.open_file_btn.pack(side=tk.LEFT, expand=True, fill=tk.X)
        self.open_folder_btn = ttk.Button(file_mgmt_frame, text="Open Folder", command=self.open_loaded_folder, state=tk.DISABLED); self.open_folder_btn.pack(side=tk.LEFT, expand=True, fill=tk.X)
        details_frame = ttk.LabelFrame(self, text="File Details"); details_frame.pack(padx=10, pady=10, fill=tk.X)
        self.details_messages_label = ttk.Label(details_frame, text="Total Messages: -"); self.details_messages_label.pack(padx=5, pady=2, anchor=tk.W)
        self.details_authors_label = ttk.Label(details_frame, text="Total Authors: -"); self.details_authors_label.pack(padx=5, pady=2, anchor=tk.W)
        self.details_words_label = ttk.Label(details_frame, text="Total Words: -"); self.details_words_label.pack(padx=5, pady=2, anchor=tk.W)
        self.details_unique_words_label = ttk.Label(details_frame, text="Unique Words: -"); self.details_unique_words_label.pack(padx=5, pady=2, anchor=tk.W)
        self.details_date_range_label = ttk.Label(details_frame, text="Date Range: -"); self.details_date_range_label.pack(padx=5, pady=2, anchor=tk.W)
        self.details_size_label = ttk.Label(details_frame, text="File Size: -"); self.details_size_label.pack(padx=5, pady=2, anchor=tk.W)
        export_details_frame = ttk.LabelFrame(self, text="Export Details"); export_details_frame.pack(padx=10, pady=10, fill=tk.X)
        ttk.Button(export_details_frame, text="Preview Export Settings", command=self.show_export_settings).pack(fill=tk.X, padx=5, pady=5)
        export_frame = ttk.LabelFrame(self, text="Export"); export_frame.pack(padx=10, pady=10, fill=tk.X, side=tk.BOTTOM)
        self.compress_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(export_frame, text="Compress output to a .zip file", variable=self.compress_var).pack(padx=5, pady=(0,5))
        self.export_csv_btn = ttk.Button(export_frame, text="Export as CSV", command=lambda: self.trigger_export('csv')); self.export_csv_btn.pack(padx=5, pady=5, fill=tk.X)
        self.export_txt_btn = ttk.Button(export_frame, text="Export as TXT", command=lambda: self.trigger_export('txt')); self.export_txt_btn.pack(padx=5, pady=5, fill=tk.X)
        export_mgmt_frame = ttk.Frame(export_frame); export_mgmt_frame.pack(fill=tk.X, padx=5, pady=(0,5))
        self.open_export_btn = ttk.Button(export_mgmt_frame, text="Open Last Export", command=self.open_exported_file, state=tk.DISABLED); self.open_export_btn.pack(side=tk.LEFT, expand=True, fill=tk.X)
        self.open_export_folder_btn = ttk.Button(export_mgmt_frame, text="Open Folder", command=self.open_exported_folder, state=tk.DISABLED); self.open_export_folder_btn.pack(side=tk.LEFT, expand=True, fill=tk.X)
        ttk.Label(export_frame, text="Last Export:").pack(padx=5, pady=(10, 2), anchor=tk.W)
        self.export_preview_label = ttk.Label(export_frame, text="Size: - | Lines: -"); self.export_preview_label.pack(padx=5, pady=2, anchor=tk.W)
    
    def set_busy_state(self, is_busy):
        state = tk.DISABLED if is_busy else tk.NORMAL
        self.load_button.config(state=state); self.export_csv_btn.config(state=state); self.export_txt_btn.config(state=state)

    def select_file(self):
        filepath = filedialog.askopenfilename(title="Select a Discord CSV file", filetypes=(("CSV Files", "*.csv"), ("All files", "*.*")))
        if not filepath: return
        self.controller.start_load_file_task(filepath)

    def update_with_new_data(self, data):
        self.controller.loaded_data = data; self.controller.loaded_filepath = data['filepath']
        self.filepath_label.config(text=os.path.basename(data['filepath']))
        self.details_messages_label.config(text=f"Total Messages: {data['total_messages']}"); self.details_authors_label.config(text=f"Total Authors: {data['total_authors']}")
        self.details_words_label.config(text=f"Total Words: {data['total_words']}"); self.details_unique_words_label.config(text=f"Unique Words: {data['unique_words']}")
        self.details_date_range_label.config(text=f"Date Range: {data['date_range_days']}"); self.details_size_label.config(text=f"File Size: {data['size']}")
        self.controller.filtered_dataframe = data['dataframe']; self.controller.author_data = data['authors']
        self.controller.config_tabs.update_on_new_data()
        self.controller.start_graph_task(); self.controller.start_analytics_task()
        self.open_file_btn.config(state=tk.NORMAL); self.open_folder_btn.config(state=tk.NORMAL)

    def trigger_export(self, export_format):
        if self.controller.filtered_dataframe is None: messagebox.showwarning("Export Warning", "Please load data before exporting."); return
        save_path = filedialog.asksaveasfilename(title=f"Save {export_format.upper()} as...", filetypes=[(f"{export_format.upper()} file", f"*.{export_format}")], defaultextension=f".{export_format}")
        if not save_path: return
        compress = self.compress_var.get()
        self.controller.start_export_task(export_format, save_path, compress)
        
    def update_after_export(self, result):
        final_path = result['final_path']
        self.last_export_path = final_path
        self.open_export_btn.config(state=tk.NORMAL); self.open_export_folder_btn.config(state=tk.NORMAL)
        self.export_preview_label.config(text=f"Size: {result['final_size']} | Lines: {result['line_count']}")
        messagebox.showinfo("Export Successful", f"File successfully saved to:\n{final_path}")

    def show_export_settings(self):
        settings = self.controller.config_tabs.get_all_settings()
        if not settings: return
        msg = "CURRENT EXPORT SETTINGS\n" + "=" * 35 + "\n"
        for key, val in settings.items():
            if key in ["selected_author_ids", "nicknames"]: msg += f"{key.replace('_',' ').title()}: {len(val)} items\n"
            else: msg += f"{key.replace('_',' ').title()}: {val}\n"
        msg += f"Compress Output: {self.compress_var.get()}"
        messagebox.showinfo("Export Settings Preview", msg)

    def open_loaded_file(self): os.startfile(self.controller.loaded_filepath) if self.controller.loaded_filepath and os.path.exists(self.controller.loaded_filepath) else messagebox.showwarning("File Not Found", "The original file could not be found.")
    def open_loaded_folder(self): os.startfile(os.path.dirname(self.controller.loaded_filepath)) if self.controller.loaded_filepath and os.path.exists(self.controller.loaded_filepath) else messagebox.showwarning("Folder Not Found", "The original file's folder could not be found.")
    def open_exported_file(self): os.startfile(self.last_export_path) if self.last_export_path and os.path.exists(self.last_export_path) else messagebox.showwarning("File Not Found", "The exported file could not be found.")
    def open_exported_folder(self): os.startfile(os.path.dirname(self.last_export_path)) if self.last_export_path and os.path.exists(self.last_export_path) else messagebox.showwarning("Folder Not Found", "The export folder could not be found.")