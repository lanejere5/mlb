# load.py
"""Load data from local file or gcloud bucket."""
import os
from datetime import date
from pandas import read_parquet
from google.cloud import storage
from dotenv import load_dotenv


def mlb_data(test: bool=False):
  """Load data.

  Loads data for plotting.

  Args:
    test: if true data is loaded from local file. Otherwise it is
          loaded from a gcloud storage bucket.

  Returns:
    Pandas DataFrame whose columns are the wins over 500 plots for
    each team.
  """

  if test:
    return read_parquet('2022-05-13-mlb-records.parquet')

  load_dotenv()

  # load data from bucket
  storage_client = storage.Client()
  bucket_name = os.environ.get('MLB-DATA-BUCKET-NAME')
  blob_id = str(date.today()) + '-mlb-records.parquet'
  path = os.path.join('gs://', bucket_name, blob_id)
  return read_parquet(path)
