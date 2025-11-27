"" 
# Group Design UI – Osdag Screening Task

This project is a desktop application built using **Python Tkinter** for the **Osdag Group Design Screening Task**.  
It implements a clean and functional user interface for bridge design inputs, project location data handling, geometry modification, and exporting the final project configuration.

---

## Features

- Clean and modern Tkinter UI  
- Project Location modes:
  - **Location Lookup** (Wind, Seismic Zone/Factor, Max/Min Temperature)
  - **Custom Loading Parameters**
- Type of Structure handling (Highway / Other)
- Fully validated input fields:
  - Span
  - Carriageway Width
  - Footpath
  - Skew Angle
- Modify Additional Geometry pop-up with auto-adjust:
  - Girder spacing
  - Number of girders
  - Deck overhang width
- Material selection for:
  - Girder steel  
  - Cross bracing  
  - Deck concrete
- Export results to JSON

---

## Installation

### Requirements
- Python **3.8+**
- Tkinter (included with most Python installations)

### Run the Application
```bash
python run.py


group-design/
│── README.md
│── run.py
│── group_design/
│   ├── __init__.py
│   ├── ui.py
│   ├── data.py
│   ├── popups.py
│   └── assets/  (optional, if images/data added later)
