# pipeline.py
"""Process game data.

This module defines a sequence of functions that are applied
to the game data scraped from FanGraphs.
"""
import time
import os
from calendar import month_abbr
from datetime import datetime, date
from typing import Dict

import pandas as pd
from pybaseball import schedule_and_record
from dotenv import load_dotenv
from google.cloud import storage


divisions = {
  'al_east': ['NYY', 'TBR', 'TOR', 'BAL', 'BOS'],
  'al_central': ['CHW', 'CLE', 'DET', 'KCR', 'MIN'],
  'al_west': ['LAA', 'OAK', 'SEA', 'TEX', 'HOU'],
  'nl_east': ['ATL', 'NYM', 'PHI', 'MIA', 'WSN'],
  'nl_central': ['CHC', 'MIL', 'STL', 'PIT', 'CIN'],
  'nl_west': ['LAD', 'COL', 'ARI', 'SFG', 'SDP']
}

teams = [team for div, teams in divisions.items() for team in teams]

months = {abbr: i + 1 for i, abbr in enumerate(month_abbr[1:])}

def scrape() -> Dict[str, pd.DataFrame]:
  """Scrape 2022 team records from FanGraphs.

  Returns:
    A dictionary of raw dataframes with team abbreviations as keys.
  """
  raw_records = {}

  for team in teams[:2]:
    raw_records[team] = schedule_and_record(2022, team)
    time.sleep(2) # avoid getting blocked

  return raw_records

def preprocess(raw_records: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
  """Preprocess records.

  The raw DataFrame for each team is processed as follows.

  Columns 'Date', 'Home_Away', 'Opp', 'R', 'RA', 'Rank' are selected and 
  rows corresponding to unplayed games are dropped.

  The Date column is converted to timestamp.

  Win / loss is calculated from runs for and against.

  Args:
    raw_records: dictionary of raw DataFrames with team abbreviations as keys
                 that result from scrape().

  Returns:
    Dictionary of processed DataFrames with team abbreviations as keys.
  """
  processed = {}
  for team, data in raw_records.items():
    # select relevant columns
    processed[team] = data.loc[~data['R'].isna(), ['Date', 'Home_Away', 'Opp', 'R', 'RA', 'Rank']].copy()
    # convert date strings to timestamp
    processed[team]['Date'] = processed[team]['Date'].str.split(' ') \
    .apply(lambda x: pd.Timestamp(datetime(2022, months[x[1]], int(x[2]))))
    # calculate win / loss indicators (summing this column will produce wins over .500)
    processed[team]['W/L'] = (processed[team]['R'] - processed[team]['RA']).apply(lambda x: 1 if x > 0 else -1)
    # calculate total wins / losses
    processed[team]['wins'] = processed[team]['W/L'].apply(lambda x: 1 if x == 1 else 0).cumsum()
    processed[team]['losses'] = processed[team]['W/L'].apply(lambda x: 1 if x == -1 else 0).cumsum()
  return processed

def merge_records(processed_records: Dict[str, pd.DataFrame]) -> pd.DataFrame:
  """Merge records and generate plots.

  Win / loss columns from the processed DataFrames of each team are merged
  into a single DataFrame with a row for each date in the given time period.

  These columns are then summed to produce the 'wins over .500' values for each team.

  Args:
    processed_records: dictionary of processed DataFrames with team abbreviations as keys
                 that result from preprocess().

  Returns:
    DataFrame with a columns containing the number of wins over .500 for each team, up to yesterday.
  """
  played_season = pd.date_range(start=datetime(2022, 4, 7), end=pd.Timestamp.today() - pd.Timedelta(1, 'd'))
  wins_over_500_df = pd.DataFrame(played_season.astype('datetime64[ns]'), columns=['Date'])
  
  for team, record in processed_records.items():
    # the following groupby accounts for double headers
    wins_over_500 = record.groupby('Date', as_index=False)['W/L'].sum()
    wins_over_500.rename(columns={'W/L': team}, inplace=True)
    # accumulate values to wins over .500
    wins_over_500[team] = wins_over_500[team].cumsum()
    # merge to dataframe
    wins_over_500_df = pd.merge(
        wins_over_500_df,
        wins_over_500, 
        how='outer',
        on='Date'
    ).ffill().fillna(0)
    wins_over_500_df = wins_over_500_df.set_index('Date')
  return wins_over_500_df

def validate(data: pd.DataFrame) -> bool:
  """Validate the dataframe.

  A future version of this function will test the data
  for consistency.
  """
  return True

def store(data: pd.DataFrame, today: pd.Timestamp) -> None:
  """Put data in bucket."""
  load_dotenv()
  storage_client = storage.Client()

  bucket_name = os.environ.get('MLB-DATA-BUCKET-NAME')
  blob_id = str(today) + '-mlb-records.parquet'
  path = os.path.join('gs://', bucket_name, blob_id)
  data.to_parquet(path)


class Pipeline():
  """Pipeline class.

  This class simply provides the run() method that invokes
  the data pipeline.
  """

  def run(self) -> int:
    """Run data pipeline."""
    raw_records = scrape()
    preprocessed_records = preprocess(raw_records)
    wins_over_500_df = merge_records(preprocessed_records)
    if validate(wins_over_500_df):
      store(wins_over_500_df, date.today())
      return 200
    else:
      return 400
