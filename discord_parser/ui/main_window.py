# Authored by AI: Google's Gemini Model
import tkinter as tk
from tkinter import ttk, messagebox
from utils.logger_setup import logger
from logic.file_handler import load_csv_file
from logic.data_processor import export_data, filter_dataframe_by_date
from logic.graph_handler import create_frequency_graph
from logic.analytics_handler import get_author_summary, get_datetime_summary, get_content_summary, get_attachment_summary
import threading
import queue
import zipfile
import os
from .file_pane import FilePane
from .config_tabs import ConfigTabs
from .preview_pane import PreviewPane
from utils.timing import Timer

class App(tk.Tk):
    """Main application GUI. v1.11.1"""
    def __init__(self):
        super().__init__()
        logger.info("Initializing GUI.")
        self.title("Discord CSV Parser v1.11.1")
        self.geometry("1150x800")
        self.minsize(1000, 750)
        self.loaded_data = None; self.filtered_dataframe = None; self.graph_canvas = None
        self.task_queue = queue.Queue(); self.result_queue = queue.Queue()
        self.worker_thread = threading.Thread(target=self.worker, daemon=True); self.worker_thread.start()
        self.style = ttk.Style(self); self.style.theme_use('vista')
        self.paned_window = ttk.PanedWindow(self, orient=tk.HORIZONTAL); self.paned_window.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        status_frame = ttk.Frame(self); status_frame.pack(side=tk.BOTTOM, fill=tk.X, ipady=2)
        self.status_bar = ttk.Label(status_frame, text="Ready", relief=tk.SUNKEN, anchor=tk.W); self.status_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.progress_bar = ttk.Progressbar(status_frame, orient='horizontal', mode='determinate'); self.progress_bar.pack(side=tk.RIGHT); self.progress_bar.pack_forget()
        self.file_pane = FilePane(self.paned_window, self); self.config_tabs = ConfigTabs(self.paned_window, self); self.preview_pane = PreviewPane(self.paned_window, self)
        self.paned_window.add(self.file_pane, weight=1); self.paned_window.add(self.config_tabs, weight=3); self.paned_window.add(self.preview_pane, weight=2)
        logger.info("GUI initialization complete.")
        self.after(100, self.process_results)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def worker(self):
        while True:
            try:
                task = self.task_queue.get()
                if task is None: break
                task_name, func, args, kwargs = task
                func_kwargs = {}
                if task_name == 'export':
                    func_kwargs['progress_callback'] = lambda p, m: self.result_queue.put(('progress', (p, m)))
                result = func(*args, **func_kwargs)
                if task_name == 'export':
                    result['compress'] = kwargs.get('compress', False)
                self.result_queue.put((task_name, result))
            except Exception as e:
                self.result_queue.put(('error', e))

    def process_results(self):
        try:
            while not self.result_queue.empty():
                task_name, result = self.result_queue.get_nowait()
                if task_name == 'progress':
                    percentage, message = result
                    self.status_bar.config(text=message); self.progress_bar['value'] = percentage
                elif task_name == 'load_file':
                    self.set_ui_busy(False)
                    if result: self.file_pane.update_with_new_data(result)
                    else: messagebox.showerror("File Load Error", "Could not load the file. Check console.")
                elif task_name == 'graph': self.config_tabs.datetime_tab.display_graph(result)
                elif task_name == 'analytics': self.preview_pane.update_text(result)
                elif task_name == 'export':
                    if result and result.get("success"):
                        if result.get('compress'): self._compress_file(result)
                        else: result['final_path'] = result['save_path']
                        self.file_pane.update_after_export(result)
                        self.start_analytics_task() # Refresh analytics after export
                    else:
                        messagebox.showerror("Export Failed", f"Failed to export.\n\nError: {result.get('error', 'Unknown')}")
                    self.set_ui_busy(False)
                elif task_name == 'error':
                    self.set_ui_busy(False); logger.critical(f"Unhandled exception in worker thread: {result}", exc_info=True)
                    messagebox.showerror("Worker Thread Error", f"An unexpected error occurred:\n\n{result}")
        finally:
            self.after(100, self.process_results)

    def _compress_file(self, result):
        source_path = result['save_path']
        zip_path = os.path.splitext(source_path)[0] + '.zip'
        with Timer(f"Compressing output to {os.path.basename(zip_path)}"):
            try:
                with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                    zf.write(source_path, os.path.basename(source_path))
                os.remove(source_path)
                result['final_path'] = zip_path
                result['final_size'] = f"{os.path.getsize(zip_path) / 1024:.2f} KB (zip)"
            except Exception as e:
                logger.error(f"Failed to compress file: {e}")
                messagebox.showerror("Compression Error", f"Could not compress the output file.\n\nError: {e}")
                result['final_path'] = source_path

    def set_ui_busy(self, is_busy):
        self.file_pane.set_busy_state(is_busy)
        if is_busy: self.progress_bar.pack(side=tk.RIGHT, padx=5, pady=2); self.status_bar.config(text="Starting..."); self.progress_bar['value'] = 0
        else: self.progress_bar.pack_forget(); self.status_bar.config(text="Ready")

    def start_load_file_task(self, filepath): self.set_ui_busy(True); self.task_queue.put(('load_file', load_csv_file, (filepath,), {}))
    def start_graph_task(self):
        if self.filtered_dataframe is not None:
            scale = self.config_tabs.datetime_tab.graph_scale_var.get()
            self.task_queue.put(('graph', create_frequency_graph, (self.filtered_dataframe, scale), {}))
    
    def start_analytics_task(self):
        if self.filtered_dataframe is None or not self.preview_pane.is_live_analytics_enabled(): return
        try:
            settings = self.config_tabs.get_all_settings()
            if not settings: return
            tab_name = self.config_tabs.tab(self.config_tabs.select(), "text")
            if tab_name == "Authors": self.task_queue.put(('analytics', get_author_summary, (self.filtered_dataframe, self.author_data, settings), {}))
            elif tab_name == "Date & Time": self.task_queue.put(('analytics', get_datetime_summary, (self.filtered_dataframe,), {}))
            elif tab_name == "Content": self.task_queue.put(('analytics', get_content_summary, (self.filtered_dataframe, settings), {}))
            elif tab_name == "Attachments & Reactions": self.task_queue.put(('analytics', get_attachment_summary, (self.filtered_dataframe, settings), {}))
        except (tk.TclError, AttributeError): pass

    def start_export_task(self, export_format, save_path, compress):
        settings = self.config_tabs.get_all_settings()
        if not settings: return
        self.set_ui_busy(True)
        self.task_queue.put(('export', export_data, (self.filtered_dataframe, settings, export_format, save_path), {'compress': compress}))
    def apply_date_filter(self):
        if not self.loaded_data: messagebox.showwarning("Filter Warning", "Please load a file before applying a filter."); return
        start_date = self.config_tabs.datetime_tab.start_date_var.get(); end_date = self.config_tabs.datetime_tab.end_date_var.get()
        self.filtered_dataframe = filter_dataframe_by_date(self.loaded_data['dataframe'], start_date, end_date)
        self.start_graph_task(); self.start_analytics_task()
        messagebox.showinfo("Filter Applied", f"Data has been filtered. {len(self.filtered_dataframe)} messages remain.")
    def on_closing(self): self.task_queue.put(None); self.destroy()