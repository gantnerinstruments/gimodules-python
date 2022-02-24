from datetime import datetime 
import pytz
import pandas as pd

def append_timezone_ts_to_df(df, ts_col, new_timezone, old_timezone='Africa/Accra'):
    """Appends a column of to_new timezone converted timestamps to given Dataframe.
        'Africa/Accra' -> UTC/GMT +0
        America/Phoenix -> ts of arizona
    Args:
        df (DataFrame): 
        ts_col (String): Column name
        old_timezone ( String): Timezone of current ts
        new_timezone (String): Timezone of destination ts

    Returns:
        [DataFrame]:
    """
    
    
    # Convert strings into pytz objects
    #old_timezone = pytz.timezone(old_timezone)
    #new_timezone = pytz.timezone(new_timezone)
    
    #df = df.assign(ts_new = lambda x: (old_timezone.localize(x[ts_col]).astimezone(new_timezone)))#
    

    df['ts_c'] = pd.to_datetime(df[ts_col]/1000, unit='s')
    
    df.ts_c = df.ts_c.dt.tz_localize('UTC').dt.tz_convert(new_timezone)

    return df

def replace_ts_with_timezone_ts(df, ts_col, new_timezone, old_timezone='Africa/Accra'):
    
    df[ts_col] = pd.to_datetime(df[ts_col]/1000, unit='s')
    
    df[ts_col] = df[ts_col].dt.tz_localize('UTC').dt.tz_convert(new_timezone)
    
    return df



def ts_to_dateobj_with_timezone(ts, timezone):
    """
    Generate a datetime object with corresponding timezone from given timestamp
    As unix timestamps are always UTC (GMT+0)
    Args:
        ts ([float]): Timestamp
        timezone (String): target Timezone

    Returns:
        [datetime.datetime]: datetime object
    """
    # UTC to not take localtime into account
    date_obj = datetime.utcfromtimestamp(ts/1000) # Convert into datetime object
    
    date_obj = date_obj.astimezone(pytz.timezone(timezone)) # Apply Arizona timezone
    
    return date_obj


def aggregate_df_as_resample(df, aggregation, math_operation):
    """
    Aggregates data together by a given aggregation type e.g. ('H'(Hour) 'D'(Day))
    and uses mathematical operation on them like sum(), mean(), max()
    adds column 'datetime'
    

    Args:
        df ([DataFrame]): [description]
        aggregation ([type]): [description]
        math_operation ([String]): [description]

    Returns:
        [DataFrame]: [copied and changed dataframe]
    """

    df['datetime'] = pd.to_datetime(df['ts']/1000, unit='s')

    resample = df.set_index('datetime')
    if math_operation == 'sum':
        resample = resample.resample(aggregation).sum()
    elif math_operation == 'max':
        resample = resample.resample(aggregation).max()
    elif math_operation == 'mean':
        resample = resample.resample(aggregation).mean()

    # Reset to normal indexed DF
    resample = resample.reset_index()

    return resample

def bin_df_column_values(df, column, ratio):
    """
    Binning values together e.g. Tamd:ratio5 (23 -> 25)

    Args:
        df (DataFrame): given
        column (var): column of DF
        ratio (double): binning Ratio

    Returns:
        DataFrame: 
    """
    df[column] = pd.to_numeric(round(df[column]/ratio + 0.5) * ratio)
    
    return df