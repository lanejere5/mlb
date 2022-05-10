"""load.py"""
import os
import pandas as pd
from google.cloud import storage
from dotenv import load_dotenv


def mlb_data(test=False):

  if test:
    return pd.read_csv('2022-05-10-al-east-records.csv', index_col='Date')

  load_dotenv()

  # load data from bucket
  storage_client = storage.Client()
  bucket_name = os.environ.get('MLB-DATA-BUCKET-NAME')
  blob_id = os.environ.get('MLB-RECORD-BLOB-ID')
  path = os.path.join('gs://', bucket_name, blob_id)
  df = pd.read_csv(path, index_col='Date', encoding='utf-8')

  return df


