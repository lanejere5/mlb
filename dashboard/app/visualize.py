"""Visualize.py"""
from load import mlb_data

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from collections import OrderedDict

def postseason_race():
  df = mlb_data(test=False)
  al_division = {
      'al_east': ['NYY', 'TBR', 'TOR', 'BAL', 'BOS'],
      'al_central': ['CHW', 'CLE', 'DET', 'KCR', 'MIN'],
      'al_west': ['LAA', 'OAK', 'SEA', 'TEX', 'HOU']
  }

  division_long_name = {
      'al_east': 'AL East',
      'al_central': 'AL Central',
      'al_west': 'AL West'
  }

  season = pd.date_range(start=datetime(2022, 4, 7), end=datetime(2022, 10, 2))
  played_season = pd.to_datetime(pd.date_range(start=datetime(2022, 4, 7), end=pd.Timestamp.today()))

  # division leaders
  leaders = {}
  for div, teams in al_division.items():
      top_score = -200
      for team in teams:
          if df[team].iloc[-1] > top_score:
              leaders[div] = team
              top_score = df[team].iloc[-1]

  traces = OrderedDict()

  # add line plots of team records
  for team in df.columns:
      traces[team] = go.Scatter(
          x=df.index,
          y=df[team],
          mode='lines',
          visible=True,
          name=team
      )

  # add markers for division leaders
  for div in al_division.keys():
      traces[div] = go.Scatter(
          x=[df.index[-1]],
          y=[df[leaders[div]].iloc[-1]],
          mode='markers',
          visible=True,
          name=division_long_name[div] + " Leader"
      )

  # all button
  all_button = [
      dict(
          method='update',
          label='American League (AL)',
          visible=True,
          args=[{'visible': [True for x in traces]}]
      )
  ]

  # division buttons
  division_buttons = [
      dict(
          method='update',
          label=division_long_name[div],
          visible=True,
          args=[{'visible': [True if x in al_division[div] or x == div else False for x in traces] }]
      )
      for div in al_division.keys()
  ]

  # wildcard button
  wildcard_button = [dict(
      method='restyle',
      label='AL Wildcard',
      visible=True,
      args=[{'visible': [True if x not in leaders.values() and x not in al_division.keys() else False for x in traces]}]
  )]

  # create the layout 
  layout = go.Layout(
      updatemenus=[
          dict(
              type='dropdown',
              direction='down',
              x=1,
              y=1.15,
              showactive=True,
              buttons=all_button + division_buttons + wildcard_button
          )
      ],
      title=dict(text=f'{2022} MLB Postseason Race', x=0.5),
      showlegend=True
  )

  fig = go.Figure(data=list(traces.values()), layout=layout)

  fig.update_xaxes(range=[season.min(), season.max()])
  fig.update_yaxes(range=[df.min().min() - 5, df.max().max() + 5])

  return fig
