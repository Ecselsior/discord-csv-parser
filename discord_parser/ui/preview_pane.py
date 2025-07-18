# Authored by AI: Google's Gemini Model
import tkinter as tk
from tkinter import ttk

class PreviewPane(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, width=320)
        self.pack(fill=tk.BOTH, expand=False, side=tk.RIGHT)
        self.pack_propagate(False)
        self.controller = controller
        
        self.preview_frame = ttk.LabelFrame(self, text="Analytics Dashboard")
        self.preview_frame.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

        self.live_analytics_var = tk.BooleanVar(value=False)
        live_check = ttk.Checkbutton(self.preview_frame, text="Enable Live Analytics Preview (can be slow)", variable=self.live_analytics_var, command=self.controller.start_analytics_task)
        live_check.pack(pady=(0,5))
        
        self.preview_text = tk.Text(self.preview_frame, state='disabled', wrap='word', background="#f0f0f0", font=("Courier New", 9), borderwidth=0)
        self.preview_text.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)

    def update_text(self, text):
        self.preview_text.config(state='normal')
        self.preview_text.delete('1.0', tk.END)
        self.preview_text.insert('1.0', text)
        self.preview_text.config(state='disabled')

    def is_live_analytics_enabled(self):
        return self.live_analytics_var.get()