from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import pandas as pd
import plotly.graph_objects as go
import os
import sys
from typing import Optional

# Make rel_data importable
THIS_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(THIS_DIR, 'src')
sys.path.insert(0, SRC_DIR)
from rel_data import df_maker

# Initialize FastAPI
app = FastAPI(title="Bond Futures Dashboard")

# Mount static files
app.mount("/static", StaticFiles(directory=os.path.join(THIS_DIR, "static")), name="static")

# Load and process data on startup
data = pd.read_csv(os.path.join(THIS_DIR, 'data', 'oct_data.csv'))
df = df_maker(data)

# Build shifted datetime for plotting
df['TimeDT'] = pd.to_datetime(
    '2000-01-01 ' + df['TimeOfDay'].astype(str),
    format='%Y-%m-%d %H:%M:%S'
)
cutoff = pd.to_datetime('18:00:00', format='%H:%M:%S').time()
df['TimePlot'] = df['TimeDT'].apply(
    lambda ts: ts + pd.Timedelta(days=1) if ts.time() < cutoff else ts
)

# Label columns
df['DayStr'] = df['TradingDay'].dt.strftime('%Y-%m-%d')
df['WeekDay'] = df['TradingDay'].dt.day_name()
df['DayLabel'] = df['DayStr'] + ' - ' + df['WeekDay']

# Get metadata
min_date = pd.to_datetime(df['DayStr']).min().strftime('%Y-%m-%d')
max_date = pd.to_datetime(df['DayStr']).max().strftime('%Y-%m-%d')
unique_weekdays = sorted(df['WeekDay'].unique())


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the landing page"""
    html_path = os.path.join(THIS_DIR, "templates", "landing.html")
    if not os.path.exists(html_path):
        return "<h1>Landing page not found</h1>"
    with open(html_path, "r", encoding="utf-8") as f:
        return f.read()


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    """Serve the dashboard with chart - directly serve index.html"""
    html_path = os.path.join(THIS_DIR, "templates", "index.html")
    print(f"Dashboard route called, looking for: {html_path}")
    print(f"File exists: {os.path.exists(html_path)}")
    
    if not os.path.exists(html_path):
        return "<h1>Dashboard not found at " + html_path + "</h1>"
    
    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()
    return content


@app.get("/api/chart-data")
async def get_chart_data(
    selection_mode: str = Query(..., description="'calendar' or 'weekday'"),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    weekdays: Optional[str] = Query(None, description="Comma-separated weekdays"),
    agg_mode: str = Query("selected", description="none, selected, total, or weekday")
):
    """
    Get filtered chart data and statistics
    """
    try:
        filtered = df.copy()
        
        # Filter based on selection mode
        if selection_mode == 'calendar':
            if end_date is None:
                end_date = start_date
            
            selected_date_range = pd.date_range(start=start_date, end=end_date, freq='D')
            selected_date_strs = selected_date_range.strftime('%Y-%m-%d').tolist()
            mask = filtered['DayStr'].isin(selected_date_strs)
            filtered = filtered.loc[mask]
            mode_label = "Calendar"
            
        elif selection_mode == 'weekday':
            selected_weekdays = weekdays.split(',') if weekdays else []
            mask = filtered['WeekDay'].isin(selected_weekdays)
            filtered = filtered.loc[mask]
            mode_label = f"Weekday ({', '.join(selected_weekdays)})"
        
        filtered = filtered.sort_values('TimePlot')
        
        if filtered.empty:
            return {
                "data": {},
                "stats": {"description": "No data available for selected criteria"}
            }
        
        # Get unique day labels
        selected_days = filtered['DayLabel'].unique().tolist()
        
        # Build traces for each day
        traces = []
        for label in selected_days:
            day_df = filtered.query('DayLabel == @label')
            traces.append({
                'x': day_df['TimePlot'].dt.strftime('%Y-%m-%d %H:%M:%S').tolist(),
                'y': day_df['Relative Price'].tolist(),
                'type': 'scatter',
                'mode': 'lines',
                'name': label,
                'opacity': 0.7
            })
        
        # Add mean/SD aggregation if requested
        mean_traces = []
        if agg_mode != 'none':
            agg_df, mean_label = get_agg_df(filtered, agg_mode, selected_days)
            
            if agg_df is not None and not agg_df.empty:
                mean_curve = agg_df.groupby('TimePlot')['Relative Price'].mean().sort_index()
                sd_curve = agg_df.groupby('TimePlot')['Relative Price'].std().sort_index()
                
                # Mean trace
                mean_traces.append({
                    'x': mean_curve.index.strftime('%Y-%m-%d %H:%M:%S').tolist(),
                    'y': mean_curve.values.tolist(),
                    'type': 'scatter',
                    'mode': 'lines',
                    'name': f'{mean_label}',
                    'line': {'color': 'black', 'width': 3, 'dash': 'dot'}
                })
                
                # +1 SD
                mean_traces.append({
                    'x': sd_curve.index.strftime('%Y-%m-%d %H:%M:%S').tolist(),
                    'y': (mean_curve.values + sd_curve.values).tolist(),
                    'type': 'scatter',
                    'mode': 'lines',
                    'line': {'width': 0},
                    'showlegend': False
                })
                
                # -1 SD with fill
                mean_traces.append({
                    'x': sd_curve.index.strftime('%Y-%m-%d %H:%M:%S').tolist(),
                    'y': (mean_curve.values - sd_curve.values).tolist(),
                    'type': 'scatter',
                    'mode': 'lines',
                    'fill': 'tonexty',
                    'line': {'width': 0, 'color': 'gray'},
                    'name': f'{mean_label} ±1SD',
                    'opacity': 0.3
                })
        
        # Calculate statistics
        if agg_mode != 'none':
            agg_df, _ = get_agg_df(filtered, agg_mode, selected_days)
            if agg_df is not None and not agg_df.empty:
                sel_mean = agg_df['Relative Price'].mean()
                sel_sd = agg_df['Relative Price'].std()
                desc = (f"Mode: {agg_mode.title()} | Selection: {mode_label} | Days: {len(selected_days)} | "
                        f"Avg Relative Price: {sel_mean:.4f} | SD: {sel_sd:.4f}")
            else:
                desc = f"Selected {len(selected_days)} day(s)"
        else:
            desc = f"Showing {len(selected_days)} individual day(s) — Selection: {mode_label}"
        
        return {
            "data": {
                "traces": traces + mean_traces,
                "layout": {
                    'template': 'plotly_white',
                    'xaxis': {
                        'tickformat': '%H:%M',
                        'range': ['2000-01-01 18:00:00', '2000-01-02 17:59:00'],
                        'title': 'Time (18:00–17:59)'
                    },
                    'yaxis': {'title': 'Relative Price'},
                    'legend': {'title': {'text': 'Trading Day'}},
                    'hovermode': 'x unified',
                    'paper_bgcolor': '#ffffff',
                    'plot_bgcolor': '#ffffff',
                    'font': {'color': '#000000'}
                }
            },
            "stats": {"description": desc}
        }
    
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "data": {},
            "stats": {"description": f"Server error: {str(e)}"}
        }


def get_agg_df(filtered, agg_mode, selected_days):
    """Helper function to get aggregation dataframe"""
    if agg_mode == 'total':
        agg_df = df.copy()
        label = 'Total Mean'
    elif agg_mode == 'weekday' and len(selected_days) == 1:
        weekday = filtered['WeekDay'].iloc[0]
        agg_df = df[df['WeekDay'] == weekday].copy()
        label = f'{weekday} Mean'
    elif agg_mode == 'selected':
        agg_df = filtered.copy()
        label = 'Selected Mean'
    else:
        agg_df = None
        label = None
    return agg_df, label


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)