# Authored by AI: Google's Gemini Model
import tkinter as tk
from tkinter import ttk, messagebox
from logic.data_processor import BAD_WORDS_PATTERN
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class ConfigTabs(ttk.Notebook):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        self.authors_tab = self._create_authors_tab()
        self.datetime_tab = self._create_datetime_tab()
        self.content_tab = self._create_content_tab()
        self.attachments_tab = self._create_attachments_tab()
        
        self.add(self.authors_tab, text="Authors")
        self.add(self.datetime_tab, text="Date & Time")
        self.add(self.content_tab, text="Content")
        self.add(self.attachments_tab, text="Attachments & Reactions")

        self.bind("<<NotebookTabChanged>>", lambda e: self.controller.start_analytics_task())

    def update_on_new_data(self):
        self.datetime_tab.start_date_var.set(self.controller.loaded_data['first_date'].split(' ')[0])
        self.datetime_tab.end_date_var.set(self.controller.loaded_data['last_date'].split(' ')[0])
        self.authors_tab.sort_combo.set("By Name")
        self.authors_tab.on_sort_change()

    def get_all_settings(self):
        try:
            df = self.controller.loaded_data['dataframe']
            return {
                **self.authors_tab.get_settings(), **self.datetime_tab.get_settings(),
                **self.content_tab.get_settings(), **self.attachments_tab.get_settings(),
                "first_date_timestamp": df['Date'].min(), "last_date_timestamp": df['Date'].max()
            }
        except ValueError: messagebox.showerror("Invalid Input", "Please ensure min/max trim values are valid integers."); return None
        except (AttributeError, TypeError): messagebox.showerror("Data Error", "Cannot get settings because no data is loaded."); return None

    def _create_authors_tab(self):
        tab = ttk.Frame(self); tab.author_widgets = []
        controls_frame = ttk.Frame(tab); controls_frame.pack(fill=tk.X, padx=10, pady=10)
        ttk.Label(controls_frame, text="Sort by:").pack(side=tk.LEFT, padx=(0,5))
        tab.sort_combo = ttk.Combobox(controls_frame, state="readonly", values=["By Name", "By ID", "By Message Count"]); tab.sort_combo.pack(side=tk.LEFT)
        tab.sort_combo.bind("<<ComboboxSelected>>", lambda e: tab.on_sort_change())
        ttk.Button(controls_frame, text="Select All", command=lambda: tab.select_all(True)).pack(side=tk.RIGHT)
        ttk.Button(controls_frame, text="Deselect All", command=lambda: tab.select_all(False)).pack(side=tk.RIGHT, padx=5)
        list_frame = ttk.Frame(tab); list_frame.pack(padx=10, pady=0, fill=tk.BOTH, expand=True)
        author_canvas = tk.Canvas(list_frame, borderwidth=0); author_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=author_canvas.yview); scrollbar.pack(side=tk.RIGHT, fill="y")
        tab.scrollable_frame = ttk.Frame(author_canvas)
        author_canvas.configure(yscrollcommand=scrollbar.set); author_canvas.create_window((0, 0), window=tab.scrollable_frame, anchor="nw")
        tab.scrollable_frame.bind("<Configure>", lambda e: author_canvas.configure(scrollregion=author_canvas.bbox("all")))
        options_frame = ttk.LabelFrame(tab, text="Formatting Options"); options_frame.pack(padx=10, pady=10, fill=tk.X, side=tk.BOTTOM)
        tab.format_var = tk.StringVar(value="name")
        author_opts = {"Name Only": "name_only", "ID Only": "id_only", "Author ID & Name": "both", "Use Numeric Keys": "numeric_keys", "Use Custom Nickname": "nickname", "Anonymize": "anonymize", "Omit Author": "omit"}
        rad_cmd = lambda: [tab.update_options_state(), self.controller.start_analytics_task()]
        for text, val in author_opts.items():
            ttk.Radiobutton(options_frame, text=text, variable=tab.format_var, value=val, command=rad_cmd).pack(anchor=tk.W, padx=5)
        
        sub_options_frame = ttk.Frame(options_frame); sub_options_frame.pack(fill=tk.X, padx=20, pady=5)
        tab.create_key_var = tk.BooleanVar(value=True)
        tab.create_key_checkbutton = ttk.Checkbutton(sub_options_frame, text="Create export key file", variable=tab.create_key_var, state=tk.DISABLED); tab.create_key_checkbutton.pack(anchor=tk.W)
        tab.group_consecutive_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(sub_options_frame, text="Group consecutive messages by same author", variable=tab.group_consecutive_var).pack(anchor=tk.W, pady=2)
        tab.scrub_content_var = tk.BooleanVar(value=False)
        scrub_check = ttk.Checkbutton(sub_options_frame, text="Scrub author from message content", variable=tab.scrub_content_var, command=self.controller.start_analytics_task); scrub_check.pack(anchor=tk.W)

        def on_sort_change():
            if not self.controller.author_data: return
            sort_key = tab.sort_combo.get()
            if sort_key == "By Name": self.controller.author_data.sort(key=lambda x: x['name'].lower())
            elif sort_key == "By ID": self.controller.author_data.sort(key=lambda x: int(x['id']))
            elif sort_key == "By Message Count": self.controller.author_data.sort(key=lambda x: x['count'], reverse=True)
            populate_author_list_ui()
        def populate_author_list_ui():
            for child in tab.scrollable_frame.winfo_children(): child.destroy()
            tab.author_widgets.clear()
            for author in self.controller.author_data:
                var = tk.BooleanVar(value=True); frame = ttk.Frame(tab.scrollable_frame); frame.pack(fill='x', expand=True, padx=2, pady=1)
                check = ttk.Checkbutton(frame, text=f"{author['name']} ({author['count']} msgs)", variable=var, command=lambda: [tab.update_options_state(), self.controller.start_analytics_task()]); check.pack(side='left', fill='x', expand=True)
                entry = ttk.Entry(frame, width=20, state=tk.DISABLED); entry.pack(side='right')
                tab.author_widgets.append({'id': author['id'], 'var': var, 'entry': entry, 'name': author['name']})
            tab.update_options_state()
        def update_options_state():
            format_val = tab.format_var.get()
            is_nickname = format_val == "nickname"
            can_have_key = format_val in ["anonymize", "numeric_keys"]
            for widgets in tab.author_widgets: widgets['entry'].config(state=tk.NORMAL if is_nickname and widgets['var'].get() else tk.DISABLED)
            tab.create_key_checkbutton.config(state=tk.NORMAL if can_have_key else tk.DISABLED)
        tab.on_sort_change = on_sort_change; tab.select_all = lambda s: [w['var'].set(s) for w in tab.author_widgets] and update_options_state() and self.controller.start_analytics_task()
        tab.update_options_state = update_options_state; tab.get_selected_author_ids = lambda: [w['id'] for w in tab.author_widgets if w['var'].get()]
        tab.get_settings = lambda: {"author_format": tab.format_var.get(), "create_key_file": tab.create_key_var.get(), "selected_author_ids": tab.get_selected_author_ids(), "nicknames": {w['id']: w['entry'].get() or w['name'] for w in tab.author_widgets if w['var'].get()}, "group_consecutive": tab.group_consecutive_var.get(), "scrub_author_from_content": tab.scrub_content_var.get()}
        return tab

    def _create_datetime_tab(self):
        tab = ttk.Frame(self)
        filter_frame = ttk.LabelFrame(tab, text="Date Range Filter (Format: YYYY-MM-DD)"); filter_frame.pack(padx=10, pady=10, fill=tk.X)
        tab.start_date_var = tk.StringVar(); tab.end_date_var = tk.StringVar()
        ttk.Label(filter_frame, text="Start:").pack(side=tk.LEFT, padx=5); ttk.Entry(filter_frame, textvariable=tab.start_date_var, width=12).pack(side=tk.LEFT)
        ttk.Label(filter_frame, text="End:").pack(side=tk.LEFT, padx=5); ttk.Entry(filter_frame, textvariable=tab.end_date_var, width=12).pack(side=tk.LEFT)
        ttk.Button(filter_frame, text="Apply Filter", command=self.controller.apply_date_filter).pack(side=tk.RIGHT, padx=5)
        tab.graph_frame = ttk.LabelFrame(tab, text="Message Frequency"); tab.graph_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        graph_options_frame = ttk.LabelFrame(tab, text="Graph Scale"); graph_options_frame.pack(padx=10, pady=10, fill=tk.X)
        tab.graph_scale_var = tk.StringVar(value="day")
        for scale in ["Hour", "Day", "Week", "Month"]: ttk.Radiobutton(graph_options_frame, text=scale, variable=tab.graph_scale_var, value=scale.lower(), command=self.controller.start_graph_task).pack(side=tk.LEFT, padx=5)
        date_format_frame = ttk.LabelFrame(tab, text="Date Formatting"); date_format_frame.pack(padx=10, pady=10, fill=tk.X)
        tab.date_format_var = tk.StringVar(value="show")
        date_opts = {"Show (Timestamp)": "show", "Hide Date": "hide", "Relative (from first)": "relative_first", "Relative (from last)": "relative_last", "Unix Timestamp": "unix"}
        for text, val in date_opts.items(): ttk.Radiobutton(date_format_frame, text=text, variable=tab.date_format_var, value=val).pack(anchor=tk.W, padx=5)
        def display_graph(figure):
            if hasattr(tab, 'graph_canvas') and tab.graph_canvas: tab.graph_canvas.get_tk_widget().destroy()
            if figure: tab.graph_canvas = FigureCanvasTkAgg(figure, master=tab.graph_frame); tab.graph_canvas.draw(); tab.graph_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        tab.display_graph = display_graph
        tab.get_settings = lambda: {"date_format": tab.date_format_var.get()}
        return tab

    def _create_content_tab(self):
        tab = ttk.Frame(self)
        cmd = self.controller.start_analytics_task
        gen_format_frame = ttk.LabelFrame(tab, text="General Formatting"); gen_format_frame.pack(padx=10, pady=10, fill=tk.X)
        tab.normalize_whitespace_var = tk.BooleanVar(value=False); ttk.Checkbutton(gen_format_frame, text="Normalize whitespace (collapse multiple spaces/tabs/newlines)", variable=tab.normalize_whitespace_var, command=cmd).pack(anchor=tk.W, padx=5)
        tab.omit_brackets_var = tk.BooleanVar(value=False); ttk.Checkbutton(gen_format_frame, text="Omit brackets from generated tags (e.g., 'link' instead of '<link>')", variable=tab.omit_brackets_var, command=cmd).pack(anchor=tk.W, padx=5)
        trim_frame = ttk.LabelFrame(tab, text="Content Trimming"); trim_frame.pack(padx=10, pady=10, fill=tk.X)
        tab.trim_logic_var = tk.StringVar(value="AND"); logic_frame = ttk.Frame(trim_frame); logic_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(logic_frame, text="Keep message if it matches:").pack(side=tk.LEFT)
        ttk.Radiobutton(logic_frame, text="ALL conditions (AND)", variable=tab.trim_logic_var, value="AND", command=cmd).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(logic_frame, text="ANY condition (OR)", variable=tab.trim_logic_var, value="OR", command=cmd).pack(side=tk.LEFT, padx=5)
        tab.trim_chars_min_var = tk.StringVar(value="1"); tab.trim_chars_max_var = tk.StringVar(value="2000"); tab.trim_words_min_var = tk.StringVar(value="0"); tab.trim_words_max_var = tk.StringVar(value="1000")
        tab.trim_chars_min_enabled = tk.BooleanVar(value=True); tab.trim_chars_max_enabled = tk.BooleanVar(value=True); tab.trim_words_min_enabled = tk.BooleanVar(); tab.trim_words_max_enabled = tk.BooleanVar()
        def add_trim_row(parent, text, min_var, max_var, min_enabled_var, max_enabled_var):
            frame = ttk.Frame(parent); frame.pack(fill=tk.X, padx=5, pady=5)
            ttk.Label(frame, text=text, width=12).pack(side=tk.LEFT)
            ttk.Checkbutton(frame, text="Min:", variable=min_enabled_var, command=cmd).pack(side=tk.LEFT); ttk.Entry(frame, textvariable=min_var, width=7).pack(side=tk.LEFT)
            ttk.Checkbutton(frame, text="Max:", variable=max_enabled_var, command=cmd).pack(side=tk.LEFT, padx=(10,0)); ttk.Entry(frame, textvariable=max_var, width=7).pack(side=tk.LEFT)
        add_trim_row(trim_frame, "Characters:", tab.trim_chars_min_var, tab.trim_chars_max_var, tab.trim_chars_min_enabled, tab.trim_chars_max_enabled)
        add_trim_row(trim_frame, "Words:", tab.trim_words_min_var, tab.trim_words_max_var, tab.trim_words_min_enabled, tab.trim_words_max_enabled)
        filter_frame = ttk.LabelFrame(tab, text="Content Filtering (from bad_words.txt)"); filter_frame.pack(padx=10, pady=10, fill=tk.X)
        tab.bad_word_filter_mode = tk.StringVar(value="disabled"); tab.snip_replacement_var = tk.StringVar(value="<snip>")
        def toggle_snip_entry(): tab.snip_entry.config(state=tk.NORMAL if tab.bad_word_filter_mode.get() == 'snip_word' else tk.DISABLED); cmd()
        radio_frame = ttk.Frame(filter_frame); radio_frame.pack(fill=tk.X, padx=5)
        ttk.Radiobutton(radio_frame, text="Disabled", variable=tab.bad_word_filter_mode, value="disabled", command=toggle_snip_entry).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(radio_frame, text="Snip Word", variable=tab.bad_word_filter_mode, value="snip_word", command=toggle_snip_entry).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(radio_frame, text="Snip Message", variable=tab.bad_word_filter_mode, value="snip_message", command=toggle_snip_entry).pack(side=tk.LEFT, padx=5)
        if not BAD_WORDS_PATTERN:
            for child in filter_frame.winfo_children(): child.configure(state='disabled')
        entry_frame = ttk.Frame(filter_frame); entry_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(entry_frame, text="Replacement Text:").pack(side=tk.LEFT, padx=5)
        tab.snip_entry = ttk.Entry(entry_frame, textvariable=tab.snip_replacement_var); tab.snip_entry.pack(side=tk.LEFT, padx=5)
        toggle_snip_entry()
        url_frame = ttk.LabelFrame(tab, text="URL Formatting"); url_frame.pack(padx=10, pady=10, fill=tk.X, side=tk.BOTTOM)
        tab.shorten_urls_var = tk.BooleanVar(value=False); 
        def toggle_url_options():
            state = tk.NORMAL if tab.shorten_urls_var.get() else tk.DISABLED
            for child in tab.url_options_frame.winfo_children(): child.config(state=state)
            cmd()
        shorten_check = ttk.Checkbutton(url_frame, text="Enable URL Formatting", variable=tab.shorten_urls_var, command=toggle_url_options); shorten_check.pack(anchor=tk.W, padx=5)
        tab.url_options_frame = ttk.Frame(url_frame); tab.url_options_frame.pack(fill=tk.X, padx=20)
        tab.url_format_mode = tk.StringVar(value="tag_generic")
        ttk.Radiobutton(tab.url_options_frame, text="Generic Tags (<link>, <youtube>)", variable=tab.url_format_mode, value="tag_generic", command=cmd).pack(anchor=tk.W)
        ttk.Radiobutton(tab.url_options_frame, text="Domain Tags (<domain.com>)", variable=tab.url_format_mode, value="tag_domain", command=cmd).pack(anchor=tk.W)
        ttk.Radiobutton(tab.url_options_frame, text="Remove URL", variable=tab.url_format_mode, value="blank", command=cmd).pack(anchor=tk.W)
        toggle_url_options()
        tab.get_settings = lambda: {"trim_logic": tab.trim_logic_var.get(), "trim_chars_min_enabled": tab.trim_chars_min_enabled.get(), "trim_chars_min": int(tab.trim_chars_min_var.get()), "trim_chars_max_enabled": tab.trim_chars_max_enabled.get(), "trim_chars_max": int(tab.trim_chars_max_var.get()), "trim_words_min_enabled": tab.trim_words_min_enabled.get(), "trim_words_min": int(tab.trim_words_min_var.get()), "trim_words_max_enabled": tab.trim_words_max_enabled.get(), "trim_words_max": int(tab.trim_words_max_var.get()), "bad_word_filter_mode": tab.bad_word_filter_mode.get(), "snip_replacement": tab.snip_replacement_var.get(), "shorten_urls": tab.shorten_urls_var.get(), "url_format_mode": tab.url_format_mode.get(), "normalize_whitespace": tab.normalize_whitespace_var.get(), "omit_brackets": tab.omit_brackets_var.get()}
        return tab

    def _create_attachments_tab(self):
        tab = ttk.Frame(self)
        cmd = self.controller.start_analytics_task
        include_frame = ttk.LabelFrame(tab, text="Inclusion"); include_frame.pack(padx=10, pady=10, fill=tk.X)
        tab.include_attachments_var = tk.BooleanVar(value=True); ttk.Checkbutton(include_frame, text="Include Attachments", variable=tab.include_attachments_var, command=cmd).pack(anchor=tk.W, padx=5)
        tab.include_reactions_var = tk.BooleanVar(value=True); ttk.Checkbutton(include_frame, text="Include Reactions", variable=tab.include_reactions_var, command=cmd).pack(anchor=tk.W, padx=5)
        attach_format_frame = ttk.LabelFrame(tab, text="Attachment Formatting"); attach_format_frame.pack(padx=10, pady=10, fill=tk.X)
        tab.attach_format_var = tk.StringVar(value="tag")
        ttk.Radiobutton(attach_format_frame, text="Full Link", variable=tab.attach_format_var, value="link").pack(anchor=tk.W, padx=5)
        ttk.Radiobutton(attach_format_frame, text="Tag", variable=tab.attach_format_var, value="tag").pack(anchor=tk.W, padx=5)
        ttk.Radiobutton(attach_format_frame, text="Filename only", variable=tab.attach_format_var, value="filename").pack(anchor=tk.W, padx=5)
        ttk.Radiobutton(attach_format_frame, text="Binary (1 for yes, blank for no)", variable=tab.attach_format_var, value="binary").pack(anchor=tk.W, padx=5)
        tab.get_settings = lambda: {"include_attachments": tab.include_attachments_var.get(), "include_reactions": tab.include_reactions_var.get(), "attachment_format": tab.attach_format_var.get()}
        return tab