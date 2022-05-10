"""load.py"""
import os
import pandas as pd
from google.cloud import storage


def mlb_data(test=False):
  if test:
    return pd.read_csv('2022-05-10-al-east-records.csv', index_col='Date')

  # load data from bucket
  storage_client = storage.Client()
  bucket_name = os.environ.get('MLB-DATA-BUCKET-NAME')
  blob_id = os.environ.get('MLB-RECORD-BLOB-ID')
  path = os.path.join('gs://', bucket_name, blob_id)
  df = pd.read_csv(path, encoding='utf-8')

  return df


