Bond Futures Dashboard
A web dashboard for analyzing bond futures trading data (TUZ5, FVZ5, TYZ5) with interactive charts and date filtering.

Installation
Install dependencies:

bash
pip install -r requirements.txt
Add CSV files to the data/ folder:

TUZ5.csv

FVZ5.csv

TYZ5.csv

Run the server:

bash
python main.py
Open http://localhost:8000 in your browser

Features
Multi-ticker support (2Y, 5Y, 10Y Treasury)

Interactive intraday charts

Date range and weekday filtering

Dark/light mode toggle

Landing page with ticker previews

File Structure
text
├── main.py              # FastAPI backend
├── requirements.txt     # Dependencies
├── templates/
│   ├── index.html      # Dashboard
│   └── landing.html    # Landing page
├── data/
│   ├── TUZ5.csv
│   ├── FVZ5.csv
│   └── TYZ5.csv
└── src/
    └── rel_data.py     # Data utilities
Usage
Landing Page: Click any ticker card to view the full dashboard

Dashboard: Use the sidebar calendar to select dates, adjust filters, and toggle themes

Charts: Hover to see values, select date ranges to compare multiple days
