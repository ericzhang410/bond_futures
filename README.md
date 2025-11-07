# Bond Futures Dashboard

A full-stack web application providing comprehensive overnight rate analysis for treasury bond futures. The platform features a FastAPI REST API delivering intraday price analytics, historical data visualization, and multi-ticker comparison capabilities. Interactive charts powered by Plotly display real-time trading patterns with customizable date range and weekday filtering.

**[View Live Demo](https://bond-futures.vercel.app/)**

## Overview

The Bond Futures Dashboard offers traders and analysts a powerful tool to track, visualize, and analyze U.S. Treasury bond futures contracts with real-time intraday data, historical comparisons, and advanced statistical overlays.

## Features

### Data & Analytics
- Explore multiple bond futures tickers (TUZ5 2-Year, FVZ5 5-Year, TYZ5 10-Year, USZ25 Treasury contracts)
- Real-time intraday price tracking with time-of-day visualization
- Relative price calculations for normalized analysis
- Historical price data with comprehensive statistical analysis
- Multi-day comparison with visual overlays

### Visualization & Filtering
- Interactive calendar-based date range selection for historical analysis
- Weekday-based filtering for comparative trading day analysis
- Multiple aggregation modes: None, Selected Mean/SD, Total Mean/SD
- Mean and standard deviation overlay visualization for trend analysis
- Hover-enabled interactive data inspection on all charts
- Responsive grid layout optimized for all screen sizes

### User Experience
- Modern responsive UI built with HTML5/CSS3/JavaScript
- Dark/light mode theme toggle with persistent preference storage
- Landing page with live ticker previews showing latest trading data
- Intuitive dashboard for seamless navigation
- Real-time data updates across all visualizations

## Technology Stack

### Backend
- **FastAPI** - High-performance Python web framework
- **Python 3.8+** - Primary programming language
- **Uvicorn** - ASGI web server
- **Pandas** - Data manipulation and analysis
- **NumPy** - Numerical computing

### Frontend
- **HTML5** - Semantic markup
- **CSS3** - Responsive styling with grid layouts
- **JavaScript (Vanilla)** - Client-side interactivity
- **Plotly** - Interactive data visualization library

### Data & Deployment
- **CSV** - Data storage format
- **Vercel** - Deployment platform
