import pandas as pd
import numpy as np
_FRACTION_MAP = {
    "½": 0.5,
    "¼": 0.25,
    "¾": 0.75,
    "⅛": 0.125,
    "⅜": 0.375,
    "⅝": 0.625,
    "⅞": 0.875,
}

def parse_price(s: str) -> float:
    if pd.isna(s):
        return float("nan")
    try:
        whole_str, frac_str = s.split("-", 1)
        whole = int(whole_str)
        ticks_part = "".join(ch for ch in frac_str if ch.isdigit())
        frac_chars = "".join(ch for ch in frac_str if not ch.isdigit())
        ticks = int(ticks_part) if ticks_part else 0
        frac = sum(_FRACTION_MAP.get(ch, 0) for ch in frac_chars)
        return whole + (ticks + frac) / 32
    except Exception:
        return float("nan")

def clean_data(df:pd.DataFrame) -> pd.DataFrame:
    tmp = df.copy()
    tmp['DateTime'] = pd.to_datetime(tmp['Date'])
    excel_epoch = pd.Timestamp("1899-12-30")
    tmp['Date']  = (tmp['DateTime'] - excel_epoch).dt.total_seconds() / 86400
    tmp['Price'] = tmp['Lst Trd/Lst Prxx'].map(parse_price)
    # Return Date (serial) so trading_day will find tmp['Date']
    return tmp[['Date','Price']]
    
def time(df: pd.DataFrame) -> pd.Series:
    # Convert Date (Excel serial floats) to numeric
    date = pd.to_numeric(df['Date'], errors='coerce')
    # Extract fractional days and convert to timedelta
    frac = (date % 1).round(6)
    td = pd.to_timedelta(frac, unit='D')
    # Round to nearest minute
    td_rounded = td.dt.round('min')
    # Add to a dummy midnight timestamp and extract the time component
    dummy = pd.Timestamp('2000-01-01')
    times = (dummy + td_rounded).dt.time
    return pd.Series(times, index=df.index, name='TimeOfDay')

def trading_day(df: pd.DataFrame) -> pd.Series:
    date = pd.to_numeric(df['Date'], errors='coerce')
    time = (date % 1).round(6)
    
    date_int = date.astype(int)
    trading_date_serial = np.where(time < 0.75, date_int - 1, date_int)

    excel_epoch = pd.Timestamp('1899-12-30')
    trading_date = pd.to_datetime(excel_epoch) + pd.to_timedelta(trading_date_serial, unit='D')
    
    return pd.Series(trading_date, index=df.index, name='TradingDay')

def week_day(df: pd.DataFrame, day_col: str = 'TradingDay') -> pd.Series:
    return pd.Series(df[day_col].dt.day_name(), index=df.index, name='WeekDay')

def relative_price(df: pd.DataFrame,
                   day_col: str = 'TradingDay',
                   price_col: str = 'Price') -> pd.Series:
    # Compute the opening price per trading day (first row in each group)
    day_open = df.groupby(day_col)[price_col].transform('first')
    # Subtract the open price from each price
    rel = df[price_col] - day_open
    # Return as a named Series
    return pd.Series(rel, index=df.index, name='RelPrice')

def wkday_sd(df: pd.DataFrame, day_col: str = 'WeekDay', price_col: str = 'Relative Price') -> pd.Series:
    sd = df.groupby(day_col)[price_col].transform('std')
    return pd.Series(sd, index=df.index, name='DayStdDev')

def wkday_mean(df: pd.DataFrame, day_col: str = 'WeekDay', price_col: str = 'Relative Price') -> pd.Series:
    mean = df.groupby(day_col)[price_col].transform('mean')
    return pd.Series(mean, index=df.index, name='DayStdDev')

def df_maker(df: pd.DataFrame) -> pd.DataFrame:
    copy = clean_data(df)
    out = pd.DataFrame()
    
    # Build columns that only depend on 'copy' first
    out['Date'] = copy['Date']
    out['Price'] = copy['Price']
    out['TradingDay'] = trading_day(copy)
    out['TimeOfDay'] = time(copy)
    
    out['WeekDay'] = week_day(out, day_col='TradingDay')
    
    out['Relative Price'] = relative_price(out, day_col='TradingDay', price_col='Price')
    
    out['DaySD'] = wkday_sd(out)

    out['DayMean'] = wkday_mean(out)
    
    return out
