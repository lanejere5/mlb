# load.py
"""Load dashboard data from local file or gcloud bucket."""
import os
import json
from datetime import date, timedelta
from google.cloud import storage
from dotenv import load_dotenv
from typing import Dict


def dashboard_data(test: bool=False) -> Dict:
  """Load team records.

  Loads team records for plotting.

  Args:
    test: if false data is loaded from gcloud storage bucket.

  Returns:
    Dictionary of dashboard data. 
  """
  if test:
    with open('test-dashboard-data.json', 'r') as f:
      dashboard_data = json.loads(f.read())
    return dashboard_data

  load_dotenv()

  storage_client = storage.Client()

  bucket_name = os.environ.get('MLB-DATA-BUCKET-NAME')
  bucket = storage_client.bucket(bucket_name)

  blob_id = str(date.today()) + '-dashboard-data.json'
  blob = bucket.blob(blob_id)
  
  if not blob.exists(storage_client):
    blob_id = str(date.today() - timedelta(days=1)) + '-dashboard-data.json'
    blob = bucket.blob(blob_id)
  
  dashboard_data = json.loads(blob.download_as_string())

  return dashboard_data
