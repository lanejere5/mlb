"""Visualize.py"""
import pandas as pd
import plotly.graph_objects as go
from load import mlb_data
from datetime import datetime


def postseason_race():
  df = mlb_data()
  season = pd.date_range(start=datetime(2022, 4, 7), end=datetime(2022, 10, 2))

  traces = []
  team_indexes = {}

  for i, team in enumerate(df.columns):
      
      team_indexes[team] = i
      
      traces.append(
          go.Scatter(
              x=df.index,
              y=df[team],
              visible=True,
              name=team
          )
      )

  layout = go.Layout(
      title=dict(text='American League Postseason Race', x=0.5),
      showlegend=True
  )

  fig = go.Figure(data=traces,layout=layout)

  fig.update_xaxes(range=[season.min(), season.max()])
  fig.update_yaxes(range=[df.min().min() - 5, df.max().max() + 5])

  return fig
