"" 
import tkinter as tk
from tkinter import ttk, messagebox

from .data import float_or_none

class ModifyGeometryPopup(tk.Toplevel):
    def __init__(self, parent, carriageway_width, initial=None):
        super().__init__(parent)
        self.title("Modify Additional Geometry")
        self.resizable(False, False)
        self.grab_set()
        self.carriage = float(carriageway_width)
        self.overall = self.carriage + 5.0
        self.initial = initial or {"spacing": 3.0, "girders": 4, "overhang": 1.0}
        self.result = None
        self.updating = False

        self.v_spacing = tk.StringVar(value=f"{self.initial['spacing']:.1f}")
        self.v_girders = tk.StringVar(value=str(int(self.initial['girders'])))
        self.v_overhang = tk.StringVar(value=f"{self.initial['overhang']:.1f}")

        frm = ttk.Frame(self, padding=12)
        frm.grid(row=0, column=0, sticky="nsew")

        ttk.Label(frm, text=f"Overall width = carriageway ({self.carriage:.2f}) + 5 = {self.overall:.2f} m").grid(row=0, column=0, columnspan=2, pady=(0,8))

        ttk.Label(frm, text="Girder spacing (m)").grid(row=1, column=0, sticky="w")
        ttk.Entry(frm, textvariable=self.v_spacing, width=14).grid(row=1, column=1, pady=4)

        ttk.Label(frm, text="Number of girders").grid(row=2, column=0, sticky="w")
        ttk.Entry(frm, textvariable=self.v_girders, width=14).grid(row=2, column=1, pady=4)

        ttk.Label(frm, text="Deck overhang (m)").grid(row=3, column=0, sticky="w")
        ttk.Entry(frm, textvariable=self.v_overhang, width=14).grid(row=3, column=1, pady=4)

        ttk.Label(frm, text="Rule: (overall - overhang) / spacing = number of girders").grid(row=4, column=0, columnspan=2, pady=(6,8))

        btns = ttk.Frame(frm)
        btns.grid(row=5, column=0, columnspan=2)
        ttk.Button(btns, text="OK", command=self.on_ok).pack(side="left", padx=6)
        ttk.Button(btns, text="Cancel", command=self.destroy).pack(side="left")

        self.v_spacing.trace_add("write", lambda *a: self.on_change("spacing"))
        self.v_girders.trace_add("write", lambda *a: self.on_change("girders"))
        self.v_overhang.trace_add("write", lambda *a: self.on_change("overhang"))

    def on_change(self, who):
        if self.updating:
            return
        self.updating = True
        try:
            s = float_or_none(self.v_spacing.get())
            g = float_or_none(self.v_girders.get())
            o = float_or_none(self.v_overhang.get())
            if who == "spacing" and s and s > 0:
                o = 0.0 if o is None else o
                val = (self.overall - o) / s
                if val > 0:
                    self.v_girders.set(str(max(1, int(round(val)))))
            elif who == "girders" and g and g >= 1:
                o = 0.0 if o is None else o
                val = (self.overall - o) / g
                if val > 0:
                    self.v_spacing.set(f"{val:.1f}")
            elif who == "overhang" and o is not None:
                g = 1 if g is None else g
                if g >= 1:
                    val = (self.overall - o) / g
                    self.v_spacing.set(f"{max(0.1, val):.1f}")
        except:
            pass
        finally:
            self.updating = False

    def on_ok(self):
        try:
            s = float(self.v_spacing.get())
            g = int(float(self.v_girders.get()))
            o = float(self.v_overhang.get())
        except:
            messagebox.showerror("Error", "Enter valid numeric values.")
            return
        if s <= 0 or g <= 0 or o < 0 or s >= self.overall or o >= self.overall:
            messagebox.showerror("Error", "Values invalid or exceed overall width.")
            return
        lhs = (self.overall - o) / s
        if abs(lhs - g) > 0.5:
            messagebox.showerror("Error", "Values do not satisfy relation within tolerance.")
            return
        self.result = {"spacing": round(s,1), "girders": g, "overhang": round(o,1)}
        self.destroy()

class CustomLoadingPopup(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Custom Loading Parameters")
        self.resizable(False, False)
        self.grab_set()
        self.result = None

        frm = ttk.Frame(self, padding=10)
        frm.grid(row=0, column=0, sticky="nsew")

        # Simple editable table: local key/value pairs for required fields
        ttk.Label(frm, text="Enter custom loading values").grid(row=0, column=0, columnspan=2, pady=(0,6))

        ttk.Label(frm, text="Basic wind speed (m/s)").grid(row=1, column=0, sticky="w")
        self.v_wind = tk.StringVar(value="0"); ttk.Entry(frm, textvariable=self.v_wind).grid(row=1, column=1, pady=2)

        ttk.Label(frm, text="Seismic zone").grid(row=2, column=0, sticky="w")
        self.v_zone = tk.StringVar(value="III"); ttk.Entry(frm, textvariable=self.v_zone).grid(row=2, column=1, pady=2)

        ttk.Label(frm, text="Seismic factor").grid(row=3, column=0, sticky="w")
        self.v_factor = tk.StringVar(value="0.0"); ttk.Entry(frm, textvariable=self.v_factor).grid(row=3, column=1, pady=2)

        ttk.Label(frm, text="Max shade temp (°C)").grid(row=4, column=0, sticky="w")
        self.v_tmax = tk.StringVar(value="0"); ttk.Entry(frm, textvariable=self.v_tmax).grid(row=4, column=1, pady=2)

        ttk.Label(frm, text="Min shade temp (°C)").grid(row=5, column=0, sticky="w")
        self.v_tmin = tk.StringVar(value="0"); ttk.Entry(frm, textvariable=self.v_tmin).grid(row=5, column=1, pady=2)

        btns = ttk.Frame(frm); btns.grid(row=6, column=0, columnspan=2, pady=(8,0))
        ttk.Button(btns, text="OK", command=self.on_ok).pack(side="left", padx=6)
        ttk.Button(btns, text="Cancel", command=self.destroy).pack(side="left")

    def on_ok(self):
        try:
            w = float(self.v_wind.get())
            z = self.v_zone.get().strip() or "III"
            f = float(self.v_factor.get())
            tmax = float(self.v_tmax.get())
            tmin = float(self.v_tmin.get())
        except:
            messagebox.showerror("Error", "Enter valid numeric values.")
            return
        self.result = {"wind": w, "seismic_zone": z, "seismic_factor": f, "temp_max": tmax, "temp_min": tmin}
        self.destroy()
