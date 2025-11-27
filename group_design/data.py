import os
import json

# Built-in fallback (Option B) — 5 cities (Mumbai, Delhi, Chennai, Bengaluru, Kolkata)
DEFAULT_DB = {
    "Maharashtra": {
        "Mumbai": {"wind": 39, "seismic_zone": "III", "seismic_factor": 0.16, "temp_max": 36, "temp_min": 18},
        "Pune":   {"wind": 33, "seismic_zone": "III", "seismic_factor": 0.16, "temp_max": 34, "temp_min": 12}
    },
    "Delhi NCR": {
        "Delhi": {"wind": 39, "seismic_zone": "IV", "seismic_factor": 0.24, "temp_max": 45, "temp_min": 2}
    },
    "Tamil Nadu": {
        "Chennai": {"wind": 44, "seismic_zone": "III", "seismic_factor": 0.16, "temp_max": 40, "temp_min": 20}
    },
    "Karnataka": {
        "Bengaluru": {"wind": 33, "seismic_zone": "III", "seismic_factor": 0.16, "temp_max": 35, "temp_min": 12}
    },
    "West Bengal": {
        "Kolkata": {"wind": 44, "seismic_zone": "III", "seismic_factor": 0.16, "temp_max": 39, "temp_min": 18}
    }
}

def find_project_root():
    # assume this file is in group_design/
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

def load_external_db():
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    candidate = os.path.join(root, "data", "external_db.json")
    if os.path.exists(candidate):
        try:
            with open(candidate, "r", encoding="utf-8") as f:
                db = json.load(f)
            if isinstance(db, dict) and db:
                return db
        except Exception:
            pass
    return DEFAULT_DB

def float_or_none(s):
    try:
        return float(s)
    except:
        return None

def show_error(msg):
    # used by UI/popups for consistency — import from data to avoid circular UI imports
    try:
        from tkinter import messagebox
        messagebox.showerror("Error", msg)
    except:
        print("Error:", msg)
