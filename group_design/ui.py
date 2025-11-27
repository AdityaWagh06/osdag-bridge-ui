# group_design/ui.py
import os
import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from .data import load_external_db, float_or_none
from .popups import ModifyGeometryPopup, CustomLoadingPopup

DB = load_external_db()
IMG_PATH = os.path.join(os.path.dirname(__file__), "..", "assets", "bridge_section.png")


class ScrollableFrame(ttk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0, bg="#F5F7FB")
        self.vsb = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vsb.set)
        self.interior = ttk.Frame(self.canvas)

        self.vsb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self._window = self.canvas.create_window((0, 0), window=self.interior, anchor="nw")

        self.interior.bind("<Configure>", self._on_interior_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)

    def _on_interior_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        # Keep interior width equal to canvas width
        canvas_width = event.width
        self.canvas.itemconfigure(self._window, width=canvas_width)


class GroupDesignApp(tk.Tk):
    def __init__(self):
        super().__init__()

        W, H = 1000, 720
        self.W, self.H = W, H
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        x, y = max(0, (sw - W) // 2), max(0, (sh - H) // 2)
        self.geometry(f"{W}x{H}+{x}+{y}")
        self.minsize(920, 600)
        self.title("Group Design — Osdag Screening Task")

        self.bg = "#F5F7FB"
        self.card_bg = "#FFFFFF"
        self.header_bg = "#0b2140"
        self.header_fg = "#FFFFFF"
        self.text_primary = "#0f1724"
        self.muted = "#6b7280"
        self.primary = "#1e40af"
        self.primary_dark = "#11307a"
        self.success = "#059669"

        self.configure(bg=self.bg)

        self._init_vars()
        self._setup_style()
        self._build_ui()

        self.populate_states()
        self.update_type_enabling()

    def _init_vars(self):
        self.location_mode = tk.StringVar(value="location")
        self.type_structure = tk.StringVar(value="Highway")
        defaults = {
            "span": "30",
            "carriage": "10",
            "footpath": "None",
            "skew": "0",
            "girder_grade": "E250",
            "bracing_grade": "E250",
            "deck_grade": "M25",
            "state": "",
            "district": "",
            "wind": "",
            "seismic_zone": "",
            "seismic_factor": "",
            "tmax": "",
            "tmin": "",
            "live": "5"
        }
        self.vars = {k: tk.StringVar(value=v) for k, v in defaults.items()}
        self.project_data = {}

    def _setup_style(self):
        s = ttk.Style(self)
        try:
            s.theme_use("clam")
        except Exception:
            pass

        s.configure("Card.TFrame", background=self.card_bg, relief="flat")
        s.configure("Header.TFrame", background=self.header_bg)
        s.configure("Header.TLabel", background=self.header_bg, foreground=self.header_fg,
                    font=("Segoe UI", 16, "bold"))
        s.configure("SubHeader.TLabel", background=self.header_bg, foreground=self.header_fg,
                    font=("Segoe UI", 10))
        s.configure("Field.TLabel", background=self.card_bg, foreground=self.text_primary,
                    font=("Segoe UI", 10))
        s.configure("Muted.TLabel", background=self.card_bg, foreground=self.muted, font=("Segoe UI", 9))
        s.configure("Primary.TButton", font=("Segoe UI", 10, "bold"), foreground="white", padding=6)
        s.map("Primary.TButton", background=[("!disabled", self.primary), ("active", self.primary_dark)])
        s.configure("Secondary.TButton", font=("Segoe UI", 10), padding=6)

    def _build_ui(self):
        header = ttk.Frame(self, style="Header.TFrame")
        header.grid(row=0, column=0, columnspan=2, sticky="ew", padx=12, pady=12)
        header.grid_columnconfigure(0, weight=1)

        left_header = ttk.Frame(header, style="Header.TFrame")
        left_header.grid(row=0, column=0, sticky="w", padx=8, pady=(8, 4))
        ttk.Label(left_header, text="Group Design", style="Header.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(left_header, text="Desktop UI for Osdag screening task", style="SubHeader.TLabel").grid(
            row=1, column=0, sticky="w", pady=(2, 0))

        action_frame = ttk.Frame(header, style="Header.TFrame")
        action_frame.grid(row=0, column=1, sticky="e", padx=8, pady=(8, 4))
        ttk.Button(action_frame, text="Calculate", command=self.on_calculate, style="Primary.TButton").grid(row=0, column=0, padx=(6, 6))
        ttk.Button(action_frame, text="Export Project JSON", command=self.export_project, style="Primary.TButton").grid(row=0, column=1, padx=(6, 6))
        ttk.Button(action_frame, text="Clear", command=self.on_clear, style="Secondary.TButton").grid(row=0, column=2, padx=(6, 4))

        main = ttk.Frame(self, style="Card.TFrame", padding=12)
        main.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=12, pady=(0, 12))
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        main.grid_columnconfigure(0, weight=3)
        main.grid_columnconfigure(1, weight=1)

        left_container = ScrollableFrame(main)
        left_container.grid(row=0, column=0, sticky="nsew", padx=(0, 12), pady=0)
        left_container.interior.grid_columnconfigure(0, weight=1)

        notebook = ttk.Notebook(left_container.interior)
        notebook.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)
        tab_basic = ttk.Frame(notebook, padding=12)
        notebook.add(tab_basic, text="Basic Inputs")
        notebook.add(ttk.Frame(notebook), text="Additional Inputs")

        for c in range(4):
            tab_basic.grid_columnconfigure(c, weight=1, uniform="col")

        frm_type = ttk.LabelFrame(tab_basic, text="Type of Structure", padding=8)
        frm_type.grid(row=0, column=0, columnspan=4, sticky="ew", pady=(0, 8))
        ttk.Radiobutton(frm_type, text="Highway", variable=self.type_structure, value="Highway",
                        command=self.on_type_change).grid(row=0, column=0, sticky="w", padx=6, pady=2)
        ttk.Radiobutton(frm_type, text="Other", variable=self.type_structure, value="Other",
                        command=self.on_type_change).grid(row=0, column=1, sticky="w", padx=6, pady=2)

        frm_loc = ttk.LabelFrame(tab_basic, text="Project Location", padding=8)
        frm_loc.grid(row=1, column=0, columnspan=4, sticky="ew", pady=(0, 8))
        frm_loc.grid_columnconfigure(1, weight=1)
        frm_loc.grid_columnconfigure(3, weight=1)

        ttk.Radiobutton(frm_loc, text="Enter Location Name", variable=self.location_mode, value="location",
                        command=self.on_location_mode).grid(row=0, column=0, sticky="w", pady=2, padx=4)
        ttk.Radiobutton(frm_loc, text="Custom Loading", variable=self.location_mode, value="custom",
                        command=self.on_location_mode).grid(row=0, column=1, sticky="w", pady=2, padx=4)
        self.btn_custom = ttk.Button(frm_loc, text="Open Custom", command=self.open_custom_popup,
                                     style="Secondary.TButton")
        self.btn_custom.grid(row=0, column=3, sticky="e", padx=4)

        ttk.Label(frm_loc, text="State:", style="Field.TLabel").grid(row=1, column=0, sticky="w", pady=6, padx=4)
        self.cb_state = ttk.Combobox(frm_loc, state="readonly", textvariable=self.vars["state"])
        self.cb_state.grid(row=1, column=1, columnspan=3, sticky="ew", padx=4, pady=6)
        self.cb_state.bind("<<ComboboxSelected>>", lambda e: self.on_state_selected())

        ttk.Label(frm_loc, text="District:", style="Field.TLabel").grid(row=2, column=0, sticky="w", pady=6, padx=4)
        self.cb_district = ttk.Combobox(frm_loc, state="readonly", textvariable=self.vars["district"])
        self.cb_district.grid(row=2, column=1, columnspan=3, sticky="ew", padx=4, pady=6)
        self.cb_district.bind("<<ComboboxSelected>>", lambda e: self.on_district_selected())

        info = ttk.Frame(frm_loc)
        info.grid(row=3, column=0, columnspan=4, sticky="ew", pady=(6, 0))
        info.grid_columnconfigure(1, weight=1)
        ttk.Label(info, text="Wind (m/s):", style="Muted.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(info, textvariable=self.vars["wind"], foreground=self.success).grid(row=0, column=1, sticky="w", padx=(6, 18))
        ttk.Label(info, text="Zone:", style="Muted.TLabel").grid(row=0, column=2, sticky="w")
        ttk.Label(info, textvariable=self.vars["seismic_zone"], foreground=self.success).grid(row=0, column=3, sticky="w", padx=(6, 18))
        ttk.Label(info, text="Factor:", style="Muted.TLabel").grid(row=0, column=4, sticky="w")
        ttk.Label(info, textvariable=self.vars["seismic_factor"], foreground=self.success).grid(row=0, column=5, sticky="w", padx=(6, 0))

        geom = ttk.LabelFrame(tab_basic, text="Geometric Details", padding=8)
        geom.grid(row=2, column=0, columnspan=4, sticky="ew", pady=(0, 8))
        geom.grid_columnconfigure(1, weight=1)
        geom.grid_columnconfigure(3, weight=1)

        ttk.Label(geom, text="Span (m):", style="Field.TLabel").grid(row=0, column=0, sticky="w", pady=6, padx=4)
        ttk.Entry(geom, textvariable=self.vars["span"], width=14).grid(row=0, column=1, sticky="w", pady=6, padx=4)

        ttk.Label(geom, text="Footpath:", style="Field.TLabel").grid(row=0, column=2, sticky="w", pady=6, padx=4)
        ttk.Combobox(geom, values=("None", "Single-sided", "Both"), textvariable=self.vars["footpath"],
                     state="readonly", width=14).grid(row=0, column=3, sticky="w", pady=6, padx=4)

        ttk.Label(geom, text="Carriageway width (m):", style="Field.TLabel").grid(row=1, column=0, sticky="w", pady=6, padx=4)
        ttk.Entry(geom, textvariable=self.vars["carriage"], width=14).grid(row=1, column=1, sticky="w", pady=6, padx=4)

        ttk.Label(geom, text="Skew (°):", style="Field.TLabel").grid(row=1, column=2, sticky="w", pady=6, padx=4)
        ttk.Entry(geom, textvariable=self.vars["skew"], width=14).grid(row=1, column=3, sticky="w", pady=6, padx=4)

        ttk.Label(geom, text="Live load (kN/m):", style="Field.TLabel").grid(row=2, column=0, sticky="w", pady=6, padx=4)
        ttk.Entry(geom, textvariable=self.vars["live"], width=14).grid(row=2, column=1, sticky="w", pady=6, padx=4)

        ttk.Button(geom, text="Modify Additional Geometry", command=self.open_modify_geometry,
                   style="Secondary.TButton").grid(row=3, column=0, columnspan=4, sticky="w", padx=4, pady=(8, 0))

        mat = ttk.LabelFrame(tab_basic, text="Material Inputs", padding=8)
        mat.grid(row=3, column=0, columnspan=4, sticky="ew", pady=(0, 8))
        mat.grid_columnconfigure(1, weight=1)
        ttk.Label(mat, text="Girder steel:", style="Field.TLabel").grid(row=0, column=0, sticky="w", padx=4, pady=6)
        ttk.Combobox(mat, values=("E250", "E350", "E450"), textvariable=self.vars["girder_grade"], state="readonly").grid(row=0, column=1, sticky="w", padx=4, pady=6)
        ttk.Label(mat, text="Cross bracing:", style="Field.TLabel").grid(row=1, column=0, sticky="w", padx=4, pady=6)
        ttk.Combobox(mat, values=("E250", "E350", "E450"), textvariable=self.vars["bracing_grade"], state="readonly").grid(row=1, column=1, sticky="w", padx=4, pady=6)
        ttk.Label(mat, text="Deck concrete:", style="Field.TLabel").grid(row=0, column=2, sticky="w", padx=4, pady=6)
        ttk.Combobox(mat, values=("M25", "M30", "M35", "M40", "M45", "M50", "M55", "M60"), textvariable=self.vars["deck_grade"], state="readonly").grid(row=0, column=3, sticky="w", padx=4, pady=6)

        right = ttk.Frame(main, style="Card.TFrame")
        right.grid(row=0, column=1, sticky="nsew")
        right.grid_rowconfigure(2, weight=1)
        ttk.Label(right, text="Reference", font=("Segoe UI", 11, "bold")).grid(row=0, column=0, sticky="w", padx=12, pady=(8, 6))

        if os.path.exists(IMG_PATH):
            try:
                from PIL import Image, ImageTk
                im = Image.open(IMG_PATH)
                im.thumbnail((320, 260), Image.LANCZOS)
                self._ref_img = ImageTk.PhotoImage(im)
                ttk.Label(right, image=self._ref_img).grid(row=1, column=0, padx=12, pady=(0, 10))
            except Exception:
                ttk.Label(right, text="(Image load error)", style="Muted.TLabel").grid(row=1, column=0, padx=12, pady=(0, 10))
        else:
            ttk.Label(right, text="(Place bridge_section.png in assets/ to show image)", style="Muted.TLabel").grid(row=1, column=0, padx=12, pady=(0, 10))

        ttk.Label(right, text="Values from selected location appear here.", style="Muted.TLabel", wraplength=300).grid(row=2, column=0, padx=12, pady=6)

        self.results_frame = ttk.LabelFrame(right, text="Results (Simplified)", padding=8)
        self.results_frame.grid(row=3, column=0, sticky="ew", padx=12, pady=(8, 12))
        self.res_labels = {}
        RROWS = [
            ("Deck self-weight (kN):", "deck_self_weight_kN"),
            ("Uniform load (kN/m):", "uniform_load_kN_per_m"),
            ("Total moment (kN·m):", "total_moment_kN_m"),
            ("Total shear (kN):", "total_shear_kN"),
            ("Per-girder M / V:", "per_girder_MV")
        ]
        for i, (title, key) in enumerate(RROWS):
            ttk.Label(self.results_frame, text=title, style="Field.TLabel").grid(row=i, column=0, sticky="w", padx=6, pady=4)
            lbl = ttk.Label(self.results_frame, text="—", style="Muted.TLabel")
            lbl.grid(row=i, column=1, sticky="e", padx=6, pady=4)
            self.res_labels[key] = lbl

        self.status = ttk.Label(self, text="", background=self.bg, foreground=self.text_primary)
        self.status.grid(row=2, column=0, columnspan=2, sticky="ew", padx=12, pady=(6, 12))

    # ----- data & events -----
    def populate_states(self):
        states = list(DB.keys())
        if not states:
            self.cb_state['values'] = []
            return
        self.cb_state['values'] = states
        self.vars["state"].set(states[0])
        self.on_state_selected()

    def on_state_selected(self):
        st = self.vars["state"].get()
        if st and st in DB:
            districts = list(DB[st].keys())
            self.cb_district['values'] = districts
            if districts:
                self.vars["district"].set(districts[0])
                self.on_district_selected()

    def on_district_selected(self):
        st = self.vars["state"].get(); d = self.vars["district"].get()
        if st in DB and d in DB[st]:
            data = DB[st][d]
            self.vars["wind"].set(str(data.get("wind", "")))
            self.vars["seismic_zone"].set(str(data.get("seismic_zone", "")))
            self.vars["seismic_factor"].set(str(data.get("seismic_factor", "")))
            self.vars["tmax"].set(str(data.get("temp_max", "")))
            self.vars["tmin"].set(str(data.get("temp_min", "")))

    def on_location_mode(self):
        if self.location_mode.get() == "custom":
            self.cb_state.configure(state="disabled")
            self.cb_district.configure(state="disabled")
            for k in ("wind", "seismic_zone", "seismic_factor", "tmax", "tmin"):
                self.vars[k].set("")
            self.status.config(text="Custom loading mode active")
        else:
            self.cb_state.configure(state="readonly")
            self.cb_district.configure(state="readonly")
            self.on_district_selected()
            self.status.config(text="")

    def open_custom_popup(self):
        p = CustomLoadingPopup(self)
        self.wait_window(p)
        if getattr(p, "result", None):
            r = p.result
            self.vars["wind"].set(str(r["wind"]))
            self.vars["seismic_zone"].set(str(r["seismic_zone"]))
            self.vars["seismic_factor"].set(str(r["seismic_factor"]))
            self.vars["tmax"].set(str(r["temp_max"]))
            self.vars["tmin"].set(str(r["temp_min"]))
            self.status.config(text="Custom loading parameters applied.")

    def on_type_change(self):
        self.update_type_enabling()
        if self.type_structure.get() == "Other":
            messagebox.showinfo("Note", "Other structures not included. Inputs are disabled.")

    def update_type_enabling(self):
        enable = (self.type_structure.get() == "Highway")
        if not hasattr(self, "vars"):
            return
        if not enable:
            for k in ("span", "carriage", "footpath", "skew", "girder_grade", "bracing_grade", "deck_grade"):
                self.vars[k].set("")
            self.status.config(text="Other structure selected — inputs disabled.")
        else:
            self.status.config(text="")

    def open_modify_geometry(self):
        c = float_or_none(self.vars["carriage"].get())
        if c is None:
            messagebox.showerror("Error", "Enter valid carriageway width first.")
            return
        p = ModifyGeometryPopup(self, carriageway_width=c, initial=self.project_data.get("modify_geometry"))
        self.wait_window(p)
        if getattr(p, "result", None):
            self.project_data["modify_geometry"] = p.result
            self.status.config(text=f"Modify geometry saved: {p.result}")

    def on_calculate(self):
        try:
            span = float(self.vars["span"].get())
            carriage = float(self.vars["carriage"].get())
            girders = 4
            mg = self.project_data.get("modify_geometry")
            if isinstance(mg, dict) and mg.get("girders"):
                try:
                    girders = int(mg.get("girders"))
                except Exception:
                    girders = 4
            live = float(self.vars["live"].get())
            if span <= 0 or carriage <= 0 or girders <= 0 or live < 0:
                raise ValueError
        except Exception:
            messagebox.showerror("Invalid input", "Enter valid positive numbers for span, carriage, girders and live load.")
            return

        deck_thickness = 0.2
        density_conc = 25.0
        area = span * carriage
        self_weight = density_conc * deck_thickness * area
        uniform_load = (self_weight / span) + live
        moment = uniform_load * span ** 2 / 8.0
        shear = uniform_load * span / 2.0
        per_girder_m = moment / max(1, int(girders))
        per_girder_v = shear / max(1, int(girders))

        self.res_labels["deck_self_weight_kN"].config(text=f"{self_weight:.2f}")
        self.res_labels["uniform_load_kN_per_m"].config(text=f"{uniform_load:.2f}")
        self.res_labels["total_moment_kN_m"].config(text=f"{moment:.2f}")
        self.res_labels["total_shear_kN"].config(text=f"{shear:.2f}")
        self.res_labels["per_girder_MV"].config(text=f"{per_girder_m:.2f} / {per_girder_v:.2f}")

        self.status.config(text="Calculated results updated.")

    def export_project(self):
        try:
            span = float(self.vars["span"].get())
        except Exception:
            messagebox.showerror("Error", "Enter valid span.")
            return
        if not (20 <= span <= 45):
            messagebox.showerror("Error", "Span outside 20-45 m.")
            return
        try:
            carriage = float(self.vars["carriage"].get())
        except Exception:
            messagebox.showerror("Error", "Enter valid carriageway width.")
            return
        if not (carriage >= 4.25 and carriage < 24):
            messagebox.showerror("Error", "Carriageway width must be ≥4.25 and <24 m.")
            return
        try:
            skew = float(self.vars["skew"].get())
        except Exception:
            messagebox.showerror("Error", "Enter valid skew angle.")
            return
        if abs(skew) > 15:
            if not messagebox.askyesno("Warning", "Skew outside ±15°. Continue?"):
                return

        out = {
            "type_of_structure": self.type_structure.get(),
            "location_mode": self.location_mode.get(),
            "state": self.vars["state"].get(),
            "district": self.vars["district"].get(),
            "wind": self.vars["wind"].get(),
            "seismic_zone": self.vars["seismic_zone"].get(),
            "seismic_factor": self.vars["seismic_factor"].get(),
            "temp_max": self.vars["tmax"].get(),
            "temp_min": self.vars["tmin"].get(),
            "geometric": {
                "span": span,
                "carriageway_width": carriage,
                "footpath": self.vars["footpath"].get(),
                "skew": skew,
                "live_load": float(self.vars["live"].get())
            },
            "materials": {
                "girder_steel": self.vars["girder_grade"].get(),
                "bracing_steel": self.vars["bracing_grade"].get(),
                "deck_concrete": self.vars["deck_grade"].get()
            },
            "modify_geometry": self.project_data.get("modify_geometry")
        }

        fn = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json")], initialfile="group_design_project.json")
        if not fn:
            return
        try:
            with open(fn, "w", encoding="utf-8") as f:
                json.dump(out, f, indent=2)
            messagebox.showinfo("Exported", f"Project exported to:\n{fn}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {e}")

    def on_clear(self):
        defaults = {
            "span": "30",
            "carriage": "10",
            "footpath": "None",
            "skew": "0",
            "girder_grade": "E250",
            "bracing_grade": "E250",
            "deck_grade": "M25",
            "live": "5"
        }
        for k, v in defaults.items():
            self.vars[k].set(v)
        for k in ("wind", "seismic_zone", "seismic_factor", "tmax", "tmin"):
            self.vars[k].set("")
        self.project_data.clear()
        self.status.config(text="")

if __name__ == "__main__":
    GroupDesignApp().mainloop()
