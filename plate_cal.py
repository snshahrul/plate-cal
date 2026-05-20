import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import math
import sqlite3
import pandas as pd
from reportlab.pdfgen import canvas
from datetime import datetime
from pipe_data import PIPE_SCHEDULE, SCHEDULE_NAMES, NPS_LIST

# ── Professional Color Palette ──────────────────────────────────────────
COLOR_BG         = "#f0f2f5"
COLOR_CARD       = "#ffffff"
COLOR_HEADER_BG  = "#1a2332"
COLOR_HEADER_FG  = "#ffffff"
COLOR_PRIMARY    = "#2c3e50"
COLOR_ACCENT     = "#3498db"
COLOR_ACCENT_HV  = "#2980b9"
COLOR_SUCCESS    = "#27ae60"
COLOR_SUCCESS_HV = "#219a52"
COLOR_WARNING    = "#e67e22"
COLOR_WARNING_HV = "#d35400"
COLOR_TEXT       = "#2c3e50"
COLOR_TEXT_LIGHT = "#7f8c8d"
COLOR_BORDER     = "#dcdde1"
COLOR_ENTRY_BG   = "#ffffff"
COLOR_TABLE_HEAD = "#34495e"
COLOR_TABLE_EVEN = "#f8f9fa"
COLOR_TOTAL_BG   = "#eaf2f8"

DARK_BG          = "#1a1a2e"
DARK_CARD        = "#16213e"
DARK_HEADER_BG   = "#0f0f1a"
DARK_HEADER_FG   = "#e0e0e0"
DARK_ENTRY_BG    = "#2a2a4a"
DARK_TEXT        = "#e0e0e0"
DARK_TEXT_LIGHT  = "#a0a0b0"
DARK_BORDER      = "#2a2a4a"
DARK_TABLE_HEAD  = "#0f3460"
DARK_TABLE_EVEN  = "#1a1a3e"
DARK_TOTAL_BG    = "#1a2744"

FONT_FAMILY = "Segoe UI"
FONT_ENTRY  = (FONT_FAMILY, 11)
FONT_LABEL  = (FONT_FAMILY, 11)
FONT_BUTTON = (FONT_FAMILY, 11, "bold")
FONT_TITLE  = (FONT_FAMILY, 18, "bold")
FONT_TABLE  = (FONT_FAMILY, 11)
FONT_TOTAL  = (FONT_FAMILY, 12, "bold")
FONT_SMALL  = (FONT_FAMILY, 10)

# ── Global state ────────────────────────────────────────────────────────
_is_dark = False
_result_data = {}

# ── Database ────────────────────────────────────────────────────────────
def init_database():
    conn = sqlite3.connect('steel_prices.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS steel_prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            price REAL NOT NULL
        )
    ''')
    cursor.execute("SELECT COUNT(*) FROM steel_prices")
    if cursor.fetchone()[0] == 0:
        cursor.executemany('INSERT INTO steel_prices (type, price) VALUES (?, ?)', [
            ("Mild Steel Plate (S235JR)", 5500),
            ("ASTM A36 Plate", 6000),
            ("S275JR Plate", 6200),
            ("SA516 GR.70 Plate", 5700),
            ("SA283 GR.C Plate", 5600),
            ("JIS3010 SS400 Plate", 5750),
            ("SA240 GR304 Plate", 6100),
            ("SA240 GR316 Plate", 6300),
            ("Steel Pipe", 7000),
            ("Steel Angle Bar", 6500),
            ("Steel Arc (Pipe)", 7500),
            ("SA106 GR.B Pipe", 7200),
            ("Tube BS3059 part 2 Gr.360 Pipe", 7100),
            ("GR.620 Pipe", 7800)
        ])
    conn.commit()
    conn.close()

def get_price_from_database(type_name):
    conn = sqlite3.connect('steel_prices.db')
    cursor = conn.cursor()
    cursor.execute("SELECT price FROM steel_prices WHERE type = ?", (type_name,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 7500

init_database()

# ── Core Calculation ────────────────────────────────────────────────────
def calculate_price():
    global _result_data
    try:
        selected_tab = tab_control.index(tab_control.select())
        steel_type = steel_var.get()

        if selected_tab == 0:  # Plate
            length = float(length_entry.get())
            thickness = float(thickness_entry.get())
            width = float(width_entry.get())
            volume = (length / 1000) * (width / 1000) * (thickness / 1000)
            weight_ton = volume * 7850 / 1000
            price_per_ton = get_price_from_database(steel_type)
            total_price = round(weight_ton * price_per_ton, 2)
            dims = {"Length": f"{length:,.2f} mm", "Thickness": f"{thickness:,.2f} mm", "Width": f"{width:,.2f} mm"}

        elif selected_tab == 1:  # Pipe
            length = float(length_entry_pipe.get())
            outer_dia = float(outer_diameter_entry.get())
            inner_dia = float(inner_diameter_entry.get())
            outer_radius = outer_dia / 2000
            inner_radius = inner_dia / 2000
            cross_section = math.pi * (outer_radius**2 - inner_radius**2)
            volume = cross_section * length / 1000
            weight_ton = volume * 7850 / 1000
            price_per_ton = get_price_from_database(steel_type)
            total_price = round(weight_ton * price_per_ton, 2)
            dims = {"Length": f"{length:,.2f} mm", "Outer Diameter": f"{outer_dia:,.2f} mm", "Inner Diameter": f"{inner_dia:,.2f} mm"}

        elif selected_tab == 2:  # Arc
            length = float(length_entry_arc.get())
            thickness = float(thickness_entry_arc.get())
            outer_dia = float(outer_diameter_entry_arc.get())
            inner_dia = float(inner_diameter_entry_arc.get())
            central_angle = float(central_angle_entry_arc.get())
            outer_radius = outer_dia / 2000
            inner_radius = inner_dia / 2000
            cross_section = math.pi * (outer_radius**2 - inner_radius**2)
            arc_len = outer_radius * math.radians(central_angle)
            volume = arc_len * thickness / 1000
            weight_ton = volume * 7850 / 1000
            price_per_ton = get_price_from_database(steel_type)
            total_price = round(weight_ton * price_per_ton, 2)
            dims = {"Length": f"{length:,.2f} mm", "Thickness": f"{thickness:,.2f} mm",
                    "Outer Diameter": f"{outer_dia:,.2f} mm", "Inner Diameter": f"{inner_dia:,.2f} mm",
                    "Central Angle": f"{central_angle:,.2f}\xb0"}

        elif selected_tab == 3:  # Angle Bar
            length = float(length_entry_angle.get())
            thickness = float(thickness_entry_angle.get())
            width = float(width_entry_angle.get())
            volume = (length / 1000) * (thickness / 1000) * (width / 1000) * 2
            weight_ton = volume * 7850 / 1000
            price_per_ton = get_price_from_database(steel_type)
            total_price = round(weight_ton * price_per_ton, 2)
            dims = {"Length": f"{length:,.2f} mm", "Thickness": f"{thickness:,.2f} mm", "Width": f"{width:,.2f} mm"}

        elif selected_tab == 4:  # Dished Heads
            D = float(diameter_entry_head.get())
            t = float(thickness_entry_head.get())
            SF = float(sf_entry_head.get())
            head_type = head_var.get()

            if head_type == "Hemispherical":
                dish_h = D / 2
                v_factor = math.pi / 12
                sa_factor = math.pi / 2
            elif head_type == "Ellipsoidal (2:1)":
                dish_h = D / 4
                v_factor = math.pi / 24
                sa_factor = 0.775
            elif head_type == "Torispherical (ASME F&D)":
                r = 0.06 * D
                L = D
                dish_h = L - math.sqrt((L - r)**2 - (D/2 - r)**2)
                v_factor = 0.0809
                sa_factor = 0.939
            else:  # Torispherical (DIN 28011)
                r = 0.1 * D
                L = D
                dish_h = L - math.sqrt((L - r)**2 - (D/2 - r)**2)
                v_factor = 0.1007
                sa_factor = 0.987

            V_internal = v_factor * D**3 / 1e9
            SA_dish = sa_factor * D**2 / 1e6
            SA_sf = math.pi * D * SF / 1e6
            SA_total = SA_dish + SA_sf
            volume = SA_total * t / 1000
            weight_ton = volume * 7850 / 1000
            price_per_ton = get_price_from_database(steel_type)
            total_price = round(weight_ton * price_per_ton, 2)
            dims = {
                "Head Type": head_type,
                "Inside Diameter": f"{D:,.2f} mm",
                "Thickness": f"{t:,.2f} mm",
                "Straight Flange": f"{SF:,.2f} mm",
                "Dish Height": f"{dish_h:,.2f} mm",
                "Inside Volume": f"{V_internal:.6f} m\xb3",
                "Surface Area": f"{SA_total:.4f} m\xb2",
            }

        else:
            messagebox.showwarning("Calculation Error", "Invalid tab selection.")
            return

        shape_names = ["Plate", "Pipe", "Arc", "Angle Bar", "Dished Heads"]
        vol_key = "Volume" if selected_tab != 4 else "Material Volume"
        _result_data = {
            "Steel Type": steel_type,
            "Shape": shape_names[selected_tab],
            **dims,
            vol_key: f"{volume:.6f} m\xb3",
            "Weight": f"{weight_ton:.4f} ton",
            "Price per Ton": f"RM {price_per_ton:,.2f}",
            "Total Price": f"RM {total_price:,.2f}"
        }
        update_results_table(_result_data)

    except ValueError:
        messagebox.showerror("Input Error", "Please enter valid numeric values for all dimensions.")

def update_results_table(data):
    for row in results_table.get_children():
        results_table.delete(row)
    keys = list(data.keys())
    for i, key in enumerate(keys):
        tag = "even" if i % 2 == 0 else "odd"
        if key == "Total Price":
            tag = "total"
        results_table.insert("", "end", text=key, values=(data[key],), tags=(tag,))
    if "Total Price" in data:
        status_label.config(text=f"Total: {data['Total Price']}")

# ── Export Functions ────────────────────────────────────────────────────
def _sanitize_pdf(text):
    return (text.replace("\xb3", "3").replace("\xb0", "deg").replace("\u00b7", "-"))

def export_pdf():
    if not _result_data:
        messagebox.showwarning("No Data", "Please calculate a price first.")
        return
    file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
    if not file_path:
        return
    c = canvas.Canvas(file_path)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, 780, "Steel Price Calculator - Report")
    c.setFont("Helvetica", 10)
    c.drawString(50, 760, f"Generated: {_sanitize_pdf(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}")
    c.line(50, 750, 550, 750)
    y = 730
    for key, value in _result_data.items():
        c.setFont("Helvetica-Bold" if key == "Total Price" else "Helvetica", 11)
        c.drawString(60, y, f"{_sanitize_pdf(key)}: {_sanitize_pdf(value)}")
        y -= 22
    c.save()
    messagebox.showinfo("Export", "PDF saved successfully.")

def export_csv():
    if not _result_data:
        messagebox.showwarning("No Data", "Please calculate a price first.")
        return
    file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    if not file_path:
        return
    data = {**{"Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}, **_result_data}
    df = pd.DataFrame([data])
    df.to_csv(file_path, index=False, encoding='utf-8')
    messagebox.showinfo("Export", f"CSV saved successfully.")

def clear_fields():
    global _result_data
    for entry in all_entries:
        entry.delete(0, tk.END)
    steel_var.set("Mild Steel Plate (S235JR)")
    for row in results_table.get_children():
        results_table.delete(row)
    _result_data = {}
    status_label.config(text="Ready")

# ── Theme / Dark Mode ───────────────────────────────────────────────────
def apply_theme(widget, dark):
    style = ttk.Style()
    if dark:
        bg, fg, entry_bg, entry_fg = DARK_CARD, DARK_TEXT, DARK_ENTRY_BG, DARK_TEXT
        style.configure("Treeview", background=DARK_CARD, foreground=DARK_TEXT, fieldbackground=DARK_CARD,
                        bordercolor=DARK_BORDER, font=FONT_TABLE)
        style.configure("Treeview.Heading", background=DARK_TABLE_HEAD, foreground=DARK_TEXT, font=FONT_TABLE)
        style.map("Treeview", background=[("selected", COLOR_ACCENT)])
        style.configure("TNotebook", background=DARK_BG, bordercolor=DARK_BORDER)
        style.configure("TNotebook.Tab", background=DARK_CARD, foreground=DARK_TEXT, padding=[12, 4])
        style.map("TNotebook.Tab", background=[("selected", COLOR_ACCENT)], foreground=[("selected", "#ffffff")])
        style.configure("TFrame", background=DARK_BG)
        style.configure("TLabelframe", background=DARK_CARD, foreground=DARK_TEXT)
        style.configure("TLabelframe.Label", background=DARK_BG, foreground=DARK_TEXT)
    else:
        bg, fg, entry_bg, entry_fg = COLOR_CARD, COLOR_TEXT, COLOR_ENTRY_BG, COLOR_TEXT
        style.configure("Treeview", background=COLOR_CARD, foreground=COLOR_TEXT, fieldbackground=COLOR_CARD,
                        bordercolor=COLOR_BORDER, font=FONT_TABLE)
        style.configure("Treeview.Heading", background=COLOR_TABLE_HEAD, foreground="#ffffff", font=FONT_TABLE)
        style.map("Treeview", background=[("selected", COLOR_ACCENT)])
        style.configure("TNotebook", background=COLOR_BG, bordercolor=COLOR_BORDER)
        style.configure("TNotebook.Tab", background=COLOR_CARD, foreground=COLOR_TEXT, padding=[12, 4])
        style.map("TNotebook.Tab", background=[("selected", COLOR_ACCENT)], foreground=[("selected", "#ffffff")])
        style.configure("TFrame", background=COLOR_BG)
        style.configure("TLabelframe", background=COLOR_CARD, foreground=COLOR_TEXT)
        style.configure("TLabelframe.Label", background=COLOR_BG, foreground=COLOR_TEXT)

    style.configure("Treeview", rowheight=30)
    style.configure("TButton", font=FONT_BUTTON)
    style.configure("TLabel", background=bg, foreground=fg)

    _apply_to_widget(root, dark)

def _apply_to_widget(widget, dark):
    if dark:
        bg_map = {tk.Label: DARK_CARD, tk.Entry: DARK_ENTRY_BG, tk.Button: DARK_HEADER_BG,
                  tk.Frame: DARK_BG, tk.LabelFrame: DARK_CARD}
        fg_map = {tk.Label: DARK_TEXT, tk.Entry: DARK_TEXT, tk.Button: DARK_TEXT,
                  tk.LabelFrame: DARK_TEXT}
        special = {
            header_frame: (DARK_HEADER_BG, DARK_HEADER_FG),
            header_subtitle: (DARK_HEADER_BG, DARK_TEXT_LIGHT),
            status_bar: (DARK_HEADER_BG, DARK_TEXT_LIGHT),
            result_container: (DARK_CARD, DARK_TEXT),
        }
    else:
        bg_map = {tk.Label: COLOR_CARD, tk.Entry: COLOR_ENTRY_BG, tk.Button: COLOR_ACCENT,
                  tk.Frame: COLOR_BG, tk.LabelFrame: COLOR_CARD}
        fg_map = {tk.Label: COLOR_TEXT, tk.Entry: COLOR_TEXT, tk.Button: "#ffffff",
                  tk.LabelFrame: COLOR_TEXT}
        special = {
            header_frame: (COLOR_HEADER_BG, COLOR_HEADER_FG),
            header_subtitle: (COLOR_HEADER_BG, "#8899aa"),
            status_bar: (COLOR_HEADER_BG, COLOR_TEXT_LIGHT),
            result_container: (COLOR_CARD, COLOR_TEXT),
        }

    _apply_recursive(widget, dark, bg_map, fg_map, special)

def _apply_recursive(widget, dark, bg_map, fg_map, special):
    if widget in special:
        bg, fg = special[widget]
        try:
            widget.config(bg=bg, fg=fg)
        except tk.TclError:
            try:
                widget.config(bg=bg)
            except tk.TclError:
                pass
        return
    if isinstance(widget, ttk.Combobox):
        pass
    elif isinstance(widget, tk.Label):
        widget.config(bg=bg_map.get(tk.Label, COLOR_CARD), fg=fg_map.get(tk.Label, COLOR_TEXT))
    elif isinstance(widget, tk.Entry):
        widget.config(bg=bg_map.get(tk.Entry, COLOR_ENTRY_BG), fg=fg_map.get(tk.Entry, COLOR_TEXT),
                      insertbackground=fg_map.get(tk.Entry, COLOR_TEXT))
    elif isinstance(widget, tk.Canvas):
        try:
            widget.config(bg=bg_map.get(tk.Frame, COLOR_BG))
        except tk.TclError:
            pass
    elif isinstance(widget, tk.Frame):
        try:
            widget.config(bg=bg_map.get(tk.Frame, COLOR_BG))
        except tk.TclError:
            pass
    for child in widget.winfo_children():
        _apply_recursive(child, dark, bg_map, fg_map, special)

def toggle_dark_mode():
    global _is_dark
    _is_dark = dark_mode_var.get()
    apply_theme(root, _is_dark)

# ══════════════════════════════════════════════════════════════════════════
#  UI SETUP
# ══════════════════════════════════════════════════════════════════════════
root = tk.Tk()
root.title("Steel Price Calculator")
root.geometry("820x780")
root.configure(bg=COLOR_BG)
root.minsize(700, 600)

style = ttk.Style()
style.theme_use("clam")

# ── Header ──────────────────────────────────────────────────────────────
header_frame = tk.Frame(root, bg=COLOR_HEADER_BG, height=72)
header_frame.pack(fill="x")
header_frame.pack_propagate(False)

header_title = tk.Label(header_frame, text="Steel Price Calculator",
                        font=FONT_TITLE, bg=COLOR_HEADER_BG, fg=COLOR_HEADER_FG)
header_title.pack(side="left", padx=24, pady=(8, 0))

header_subtitle = tk.Label(header_frame, text="Plate \u00b7 Pipe \u00b7 Arc \u00b7 Angle Bar \u00b7 Dished Heads",
                           font=FONT_SMALL, bg=COLOR_HEADER_BG, fg="#8899aa")
header_subtitle.pack(side="left", padx=(12, 0), pady=(12, 0))

dark_mode_var = tk.BooleanVar(value=False)
dark_toggle = ttk.Checkbutton(header_frame, text="  Dark Mode", variable=dark_mode_var,
                              command=toggle_dark_mode)
dark_toggle.pack(side="right", padx=20, pady=(22, 0))

# ── Status Bar (pack early to pin to bottom) ────────────────────────────
status_bar = tk.Frame(root, bg=COLOR_HEADER_BG, height=28)
status_bar.pack(fill="x", side="bottom")
status_bar.pack_propagate(False)
status_label = tk.Label(status_bar, text="Ready", font=FONT_SMALL,
                        bg=COLOR_HEADER_BG, fg=COLOR_TEXT_LIGHT)
status_label.pack(side="left", padx=16)
version_label = tk.Label(status_bar, text="Welded Steel Index",
                         font=(FONT_FAMILY, 9, "italic"),
                         bg=COLOR_HEADER_BG, fg="#556677")
version_label.pack(side="right", padx=16)

# ── Scrollable Content Area ─────────────────────────────────────────────
content_canvas = tk.Canvas(root, bg=COLOR_BG, highlightthickness=0)
content_canvas.pack(side="left", fill="both", expand=True)

v_scrollbar = tk.Scrollbar(root, orient="vertical", command=content_canvas.yview)
v_scrollbar.pack(side="right", fill="y")

content_canvas.configure(yscrollcommand=v_scrollbar.set)

content_frame = tk.Frame(content_canvas, bg=COLOR_BG)
cf_id = content_canvas.create_window((0, 0), window=content_frame, anchor="nw")

def _cf_configure(event):
    content_canvas.configure(scrollregion=content_canvas.bbox("all"))
content_frame.bind("<Configure>", _cf_configure)

def _cc_configure(event):
    content_canvas.itemconfig(cf_id, width=event.width)
content_canvas.bind("<Configure>", _cc_configure)

def _on_mousewheel(event):
    content_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
content_canvas.bind("<Enter>", lambda e: content_canvas.bind_all("<MouseWheel>", _on_mousewheel))
content_canvas.bind("<Leave>", lambda e: content_canvas.unbind_all("<MouseWheel>"))

# ── Steel Type Row ──────────────────────────────────────────────────────
steel_frame = tk.Frame(content_frame, bg=COLOR_BG)
steel_frame.pack(fill="x", padx=20, pady=(14, 4))

tk.Label(steel_frame, text="Steel Type:", font=FONT_LABEL, bg=COLOR_BG, fg=COLOR_TEXT
         ).pack(side="left")

steel_options = [
    "Mild Steel Plate (S235JR)", "ASTM A36 Plate", "S275JR Plate",
    "SA516 GR.70 Plate", "SA283 GR.C Plate", "JIS3010 SS400 Plate",
    "SA240 GR304 Plate", "SA240 GR316 Plate", "Steel Pipe",
    "Steel Angle Bar", "Steel Arc (Pipe)", "SA106 GR.B Pipe",
    "Tube BS3059 part 2 Gr.360 Pipe", "GR.620 Pipe"
]
steel_var = tk.StringVar(value=steel_options[0])
steel_dropdown = ttk.Combobox(steel_frame, textvariable=steel_var, values=steel_options,
                              state="readonly", font=FONT_ENTRY, width=40)
steel_dropdown.pack(side="left", padx=(10, 0))

# ── Tab Control ─────────────────────────────────────────────────────────
tab_control = ttk.Notebook(content_frame)
tab_control.pack(fill="x", padx=20, pady=(8, 0))

tab_names = ["Plate", "Pipe", "Arc", "Angle Bar", "Dished Heads"]
tabs = {}
for name in tab_names:
    f = ttk.Frame(tab_control)
    tab_control.add(f, text=name)
    f.columnconfigure(0, weight=1)
    tabs[name] = f

tab_plate   = tabs["Plate"]
tab_pipe    = tabs["Pipe"]
tab_arc     = tabs["Arc"]
tab_angle   = tabs["Angle Bar"]
tab_head    = tabs["Dished Heads"]

head_types = [
    "Hemispherical",
    "Ellipsoidal (2:1)",
    "Torispherical (ASME F&D)",
    "Torispherical (DIN 28011)"
]
head_var = tk.StringVar(value=head_types[0])

# ── Helper to build input fields inside a tab ───────────────────────────
all_entries = []

def add_field(parent, label, row, default=""):
    f = tk.Frame(parent, bg=COLOR_CARD)
    f.grid(row=row, column=0, columnspan=2, sticky="ew", padx=14, pady=3)
    f.columnconfigure(0, weight=1)
    f.columnconfigure(1, weight=2)
    lbl = tk.Label(f, text=label, font=FONT_LABEL, bg=COLOR_CARD, fg=COLOR_TEXT, anchor="w")
    lbl.grid(row=0, column=0, sticky="w")
    ent = tk.Entry(f, font=FONT_ENTRY, bg=COLOR_ENTRY_BG, fg=COLOR_TEXT,
                   insertbackground=COLOR_TEXT, relief="solid", bd=1)
    ent.grid(row=0, column=1, sticky="ew", padx=(10, 0))
    if default:
        ent.insert(0, default)
    all_entries.append(ent)
    return ent

# ── Plate Tab ───────────────────────────────────────────────────────────
tk.Label(tab_plate, text="Dimensions", font=(FONT_FAMILY, 12, "bold"),
         foreground=COLOR_PRIMARY).grid(row=0, column=0, columnspan=2, padx=14, pady=(10, 4), sticky="w")
length_entry       = add_field(tab_plate, "Length (mm):", 1)
thickness_entry    = add_field(tab_plate, "Thickness (mm):", 2)
width_entry        = add_field(tab_plate, "Width (mm):", 3)

# ── Pipe Tab ────────────────────────────────────────────────────────────
nps_var = tk.StringVar()
sch_var = tk.StringVar()

def update_pipe_from_schedule(*_):
    nps = nps_var.get()
    sch = sch_var.get()
    if nps and sch and nps in PIPE_SCHEDULE:
        entry = PIPE_SCHEDULE[nps]
        od = entry["od"]
        wall = entry["wall"].get(sch)
        if wall is not None:
            outer_diameter_entry.delete(0, tk.END)
            outer_diameter_entry.insert(0, f"{od:.2f}")
            inner_diameter_entry.delete(0, tk.END)
            inner_diameter_entry.insert(0, f"{od - 2*wall:.2f}")

nps_var.trace_add("write", update_pipe_from_schedule)
sch_var.trace_add("write", update_pipe_from_schedule)

pipe_sch_frame = tk.Frame(tab_pipe, bg=COLOR_CARD)
pipe_sch_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=14, pady=(10, 2))
pipe_sch_frame.columnconfigure(1, weight=1)
pipe_sch_frame.columnconfigure(3, weight=1)

tk.Label(pipe_sch_frame, text="NPS:", font=FONT_LABEL, bg=COLOR_CARD, fg=COLOR_TEXT
         ).grid(row=0, column=0, sticky="w", padx=(0, 4))
nps_drop = ttk.Combobox(pipe_sch_frame, textvariable=nps_var, values=NPS_LIST,
                        state="readonly", font=FONT_ENTRY, width=8)
nps_drop.grid(row=0, column=1, sticky="ew", padx=(0, 12))

tk.Label(pipe_sch_frame, text="Schedule:", font=FONT_LABEL, bg=COLOR_CARD, fg=COLOR_TEXT
         ).grid(row=0, column=2, sticky="w", padx=(0, 4))
sch_drop = ttk.Combobox(pipe_sch_frame, textvariable=sch_var, values=SCHEDULE_NAMES,
                        state="readonly", font=FONT_ENTRY, width=8)
sch_drop.grid(row=0, column=3, sticky="ew")

tk.Label(tab_pipe, text="Or enter manually:", font=(FONT_FAMILY, 10, "italic"),
         foreground=COLOR_TEXT_LIGHT).grid(row=1, column=0, columnspan=2, padx=14, pady=(6, 0), sticky="w")
length_entry_pipe       = add_field(tab_pipe, "Length (mm):", 2)
outer_diameter_entry    = add_field(tab_pipe, "Outer Diameter (mm):", 3)
inner_diameter_entry    = add_field(tab_pipe, "Inner Diameter (mm):", 4)

# ── Arc Tab ─────────────────────────────────────────────────────────────
tk.Label(tab_arc, text="Dimensions", font=(FONT_FAMILY, 12, "bold"),
         foreground=COLOR_PRIMARY).grid(row=0, column=0, columnspan=2, padx=14, pady=(10, 4), sticky="w")
length_entry_arc            = add_field(tab_arc, "Length (mm):", 1)
thickness_entry_arc         = add_field(tab_arc, "Thickness (mm):", 2)
outer_diameter_entry_arc    = add_field(tab_arc, "Outer Diameter (mm):", 3)
inner_diameter_entry_arc    = add_field(tab_arc, "Inner Diameter (mm):", 4)
central_angle_entry_arc     = add_field(tab_arc, "Central Angle (\xb0):", 5)

# ── Angle Bar Tab ───────────────────────────────────────────────────────
tk.Label(tab_angle, text="Dimensions", font=(FONT_FAMILY, 12, "bold"),
         foreground=COLOR_PRIMARY).grid(row=0, column=0, columnspan=2, padx=14, pady=(10, 4), sticky="w")
length_entry_angle     = add_field(tab_angle, "Length (mm):", 1)
thickness_entry_angle  = add_field(tab_angle, "Thickness (mm):", 2)
width_entry_angle      = add_field(tab_angle, "Width (mm):", 3)

# ── Dished Heads Tab ────────────────────────────────────────────────────
head_sel = tk.Frame(tab_head, bg=COLOR_CARD)
head_sel.grid(row=0, column=0, columnspan=2, sticky="ew", padx=14, pady=(10, 4))
head_sel.columnconfigure(1, weight=1)
tk.Label(head_sel, text="Head Type:", font=FONT_LABEL, bg=COLOR_CARD, fg=COLOR_TEXT
         ).grid(row=0, column=0, sticky="w")
head_drop = ttk.Combobox(head_sel, textvariable=head_var, values=head_types,
                         state="readonly", font=FONT_ENTRY, width=32)
head_drop.grid(row=0, column=1, sticky="ew", padx=(10, 0))

tk.Label(tab_head, text="Dimensions", font=(FONT_FAMILY, 12, "bold"),
         foreground=COLOR_PRIMARY).grid(row=1, column=0, columnspan=2, padx=14, pady=(10, 4), sticky="w")
diameter_entry_head    = add_field(tab_head, "Inside Diameter (mm):", 2)
thickness_entry_head   = add_field(tab_head, "Thickness (mm):", 3)
sf_entry_head          = add_field(tab_head, "Straight Flange (mm):", 4, default="0")

# ── Action Buttons ──────────────────────────────────────────────────────
btn_frame = tk.Frame(content_frame, bg=COLOR_BG)
btn_frame.pack(fill="x", padx=20, pady=(14, 0))

def make_button(parent, text, cmd, fg, bg, hv, w=16):
    btn = tk.Button(parent, text=text, command=cmd, font=FONT_BUTTON,
                    bg=bg, fg=fg, activebackground=hv, activeforeground=fg,
                    relief="flat", padx=10, pady=6, width=w, cursor="hand2")
    btn.pack(side="left", padx=(0, 8))
    return btn

btn_calc = make_button(btn_frame, "Calculate Price", calculate_price,
                       "#ffffff", COLOR_SUCCESS, COLOR_SUCCESS_HV, w=18)
btn_pdf  = make_button(btn_frame, "Export PDF", export_pdf,
                       "#ffffff", COLOR_WARNING, COLOR_WARNING_HV, w=12)
btn_csv  = make_button(btn_frame, "Export CSV", export_csv,
                       "#ffffff", COLOR_WARNING, COLOR_WARNING_HV, w=12)
btn_clr  = make_button(btn_frame, "Clear", clear_fields,
                       "#ffffff", COLOR_TEXT_LIGHT, "#95a5a6", w=10)

# ── Results Table ───────────────────────────────────────────────────────
result_container = tk.Frame(content_frame, bg=COLOR_CARD, bd=1, relief="solid", highlightbackground=COLOR_BORDER,
                            highlightthickness=1)
result_container.pack(fill="both", expand=True, padx=20, pady=(14, 0))

result_header = tk.Label(result_container, text="Calculation Results",
                         font=(FONT_FAMILY, 12, "bold"), bg=COLOR_CARD, fg=COLOR_TEXT)
result_header.pack(anchor="w", padx=14, pady=(10, 0))

columns = ("value",)
results_table = ttk.Treeview(result_container, columns=columns, show="tree headings",
                             height=9, selectmode="none")
results_table.heading("#0", text="Property")
results_table.heading("value", text="Value")
results_table.column("#0", minwidth=160, width=180, anchor="w")
results_table.column("value", minwidth=300, width=400, anchor="w")

results_table.tag_configure("even", background=COLOR_TABLE_EVEN)
results_table.tag_configure("odd", background=COLOR_CARD)
results_table.tag_configure("total", background=COLOR_TOTAL_BG, font=FONT_TOTAL)

results_table.pack(fill="both", expand=True, padx=14, pady=(6, 10))

# ── Initial theme application ───────────────────────────────────────────
apply_theme(root, False)

# ── Run ─────────────────────────────────────────────────────────────────
root.mainloop()
