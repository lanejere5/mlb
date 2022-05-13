import time
import os
from calendar import month_abbr
from datetime import datetime, date
import pandas as pd
from pybaseball import schedule_and_record
from dotenv import load_dotenv
from google.cloud import storage
import flask

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

def scrape():
  """Scrape 2022 team records from FanGraphs."""
  raw_records = {}

  for team in teams:
    raw_records[team] = schedule_and_record(2022, team)
    time.sleep(2) # avoid getting blocked

  return raw_records

def preprocess(raw_records):
  """Preprocess records."""
  processed_records = {}
  for team, record in raw_records.items():
    processed_record = record.loc[~record.R.isna(), ['Date', 'W/L']].copy()
    processed_record['Date'] = processed_record['Date'].str.split(' ') \
      .apply(lambda x: pd.Timestamp(datetime(2022, months[x[1]], int(x[2]))))
    processed_record['W/L'] = processed_record['W/L'].apply(lambda x: 1 if x == 'W' else -1)
    processed_record = processed_record.groupby('Date', as_index=False)['W/L'].sum() # account for double headers
    processed_record.rename(columns={'W/L': team}, inplace=True)
    processed_records[team] = processed_record

  return processed_records

def merge_records(processed_records):
  """Merge records into single dataframe."""
  played_season = pd.date_range(start=datetime(2022, 4, 7), end=pd.Timestamp.today())
  df = pd.DataFrame(played_season.astype('datetime64[ns]'), columns=['Date'])
  
  for team, record in processed_records.items():
    df = pd.merge(
        df,
        record,
        how='outer',
        on='Date'
    )
  return df.set_index('Date').cumsum().ffill().fillna(0)

def validate(data):
  """Validate the dataframe."""
  return True

def store(data, today):
  """Put data in bucket."""
  load_dotenv()
  storage_client = storage.Client()

  bucket_name = os.environ.get('MLB-DATA-BUCKET-NAME')
  blob_id = str(today) + '2022-05-10-mlb-records.csv'
  path = os.path.join('gs://', bucket_name, blob_id)
  data.to_csv(path)


class Pipeline():
  def run(self):
    """Run data pipeline."""
    today = date.today()
    raw_records = scrape()
    data = preprocess(raw_records)
    if validate(data):
      store(data, today)
      return 200
    else:
      return 400
