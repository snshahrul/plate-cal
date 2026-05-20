# Steel Price Calculator

Desktop (tkinter) and mobile-responsive web application for estimating steel weight and cost across common structural shapes and pressure vessel heads.

## Features

- **5 shape calculators** — Plate, Pipe, Arc (curved beam), Angle Bar, and Dished Heads
- **Dished Heads** (ASME & DIN standards):
  - Hemispherical
  - Ellipsoidal (2:1)
  - Torispherical ASME F&D (r = 0.06D)
  - Torispherical DIN 28011 Klöpperboden (r = 0.1D)
- **14 steel grades** with prices stored in SQLite (RM/ton)
- **Results table** with alternating row colours and highlighted total
- **Dark mode** with full recursive widget theming
- **Export** — PDF report or CSV file
- **Two interfaces**:
  - Desktop GUI (tkinter) — `plate_cal.py`
  - Mobile web app (Flask + responsive HTML/CSS/JS) — `web_app.py`

## Requirements

| Package     | Version |
|-------------|---------|
| Python      | ≥ 3.10  |
| pandas      | ≥ 1.5   |
| reportlab   | ≥ 4.0   |
| flask       | ≥ 3.0   |

## Installation

```bash
pip install pandas reportlab flask
```

## Usage

### Desktop App

```bash
python plate_cal.py
```

### Mobile / Web App

```bash
python web_app.py
```

Open `http://localhost:5000` in any browser (works on phone, tablet, desktop).

The database (`steel_prices.db`) is created automatically on first launch and seeded with 14 default grades.

### Workflow

1. Select a **Steel Type** from the dropdown (always visible above the tabs).
2. Choose a shape tab: **Plate**, **Pipe**, **Arc**, **Angle Bar**, or **Dished Heads**.
3. Enter dimensions in millimetres.
4. Click **Calculate Price**.
5. Results appear in the table below. The last row (Total Price) is highlighted.
6. Use **Export PDF** or **Export CSV** to save the result.

### Dished Heads — Notes

| Head Type | Standard | Dish Height | Volume Factor |
|-----------|----------|-------------|---------------|
| Hemispherical | — | D / 2 | πD³ / 12 |
| Ellipsoidal (2:1) | ASME / DIN | D / 4 | πD³ / 24 |
| Torispherical ASME F&D | ASME (r = 0.06D) | ≈ 0.169 D | 0.0809 D³ |
| Torispherical DIN 28011 | Klöpperboden (r = 0.1D) | ≈ 0.194 D | 0.1007 D³ |

The results table for Dished Heads includes:
- **Inside Volume** — fluid capacity of the head
- **Surface Area** — total outer surface (dish + straight flange)
- **Material Volume** — actual steel volume used for weight calculation
- **Dish Height** — depth of the dished portion

### Dark Mode

Toggle **Dark Mode** in the header bar. The theme applies recursively to all widgets, including the tab notebook and results table.

## Database

The file `steel_prices.db` is a local SQLite database with a single table:

```sql
CREATE TABLE steel_prices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL,
    price REAL NOT NULL
);
```

| Steel Grade | Price (RM/ton) |
|-------------|---------------|
| Mild Steel Plate (S235JR) | 5,500 |
| ASTM A36 Plate | 6,000 |
| S275JR Plate | 6,200 |
| SA516 GR.70 Plate | 5,700 |
| SA283 GR.C Plate | 5,600 |
| JIS3010 SS400 Plate | 5,750 |
| SA240 GR304 Plate | 6,100 |
| SA240 GR316 Plate | 6,300 |
| Steel Pipe | 7,000 |
| Steel Angle Bar | 6,500 |
| Steel Arc (Pipe) | 7,500 |
| SA106 GR.B Pipe | 7,200 |
| Tube BS3059 part 2 Gr.360 Pipe | 7,100 |
| GR.620 Pipe | 7,800 |

To add or edit prices, use any SQLite browser or:

```python
import sqlite3
conn = sqlite3.connect("steel_prices.db")
conn.execute("UPDATE steel_prices SET price = 5800 WHERE type = 'S275JR Plate'")
conn.commit()
conn.close()
```

## Pipe Wall Thickness Table

The Pipe tab includes an **Auto-fill from Schedule** feature based on ASME/ANSI B36.10 & B36.19 standards:

1. Select a **Nominal Pipe Size (NPS)** — 1/8" to 24"
2. Select a **Schedule** — 10, 20, 30, STD, 40, 60, XS, 80, 100, 120, 140, 160, XXS, 5S, 10S, 40S, 80S
3. Outer Diameter and Inner Diameter are auto-filled from the table
4. Length and manual OD/ID overrides are still available below

Schedule coverage varies by NPS (e.g., SCH 100+ only available for NPS ≥ 4). The data source is `pipe_data.py`.

## Project Structure

```
plate-cal/
├── plate_cal.py       # Desktop GUI (tkinter)
├── web_app.py         # Mobile/Web server (Flask)
├── pipe_data.py       # Pipe schedule lookup table (shared)
├── static/
│   ├── app.js         # Frontend calculator logic
│   └── style.css      # Mobile-first responsive styles
├── templates/
│   └── index.html     # Main page
├── steel_prices.db    # SQLite database (auto-created)
└── README.md
```

## Calculation Reference

**Density of steel:** 7,850 kg/m³

**Volume formulas** (all dimensions converted from mm to m):

| Shape | Volume (material) |
|-------|------------------|
| Plate | L × W × T |
| Pipe | π × (Rₒ² − Rᵢ²) × L |
| Arc | π × (Rₒ² − Rᵢ²) × θ/360° × L |
| Angle Bar | L × W × T × 2 |
| Dished Head | Surface Area × thickness |

Price = weight (tons) × price per ton (RM).
