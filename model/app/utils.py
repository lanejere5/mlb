# utils.py
"""Utils."""
import pickle
import numpy as np
from math import exp
from typing import Dict

from google.cloud import storage


def sigmoid(x: float):
  """Numerically stable sigmoid."""
  if x >= 0:
    return 1 / (1 + exp(-x))
  else:
    return exp(x) / (1 + exp(x))

def np_sigmoid(x: np.ndarray) -> np.ndarray:
  """Numerically stable sigmoid."""
  return np.where(
    x >= 0, 
    1 / (1 + np.exp(-x)), 
    np.exp(x) / (1 + np.exp(x))
  )

def load_parameters(bucket_name: str) -> Dict:
  """Load model parameters from storage."""
  storage_client = storage.Client()
  bucket = storage_client.bucket(bucket_name)

  blob_id = 'params.pkl'
  blob = bucket.blob(blob_id)

  if not blob.exists(storage_client):
    return None

  pkl = blob.download_as_string()
  params = pickle.loads(pkl)

  # log to console
  print("Loaded params:")
  print(params)
  
  return params

def save_parameters(bucket_name: str, params) -> None:
  """Save parameters to storage."""
  storage_client = storage.Client()
  bucket = storage_client.bucket(bucket_name)

  blob_id = 'params.pkl'
  blob = bucket.blob(blob_id)

  pkl = pickle.dumps(params)
  blob.upload_from_string(pkl)

  # log to console
  print("Saved params:")
  print(params)
  return
