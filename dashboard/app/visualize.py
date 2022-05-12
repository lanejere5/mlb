"""visualize.py

Generate plotly figure visualizing the postseason race.
"""
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from collections import OrderedDict

from load import mlb_data


al_division = {
  'al_east': ['NYY', 'TBR', 'TOR', 'BAL', 'BOS'],
  'al_central': ['CHW', 'CLE', 'DET', 'KCR', 'MIN'],
  'al_west': ['LAA', 'OAK', 'SEA', 'TEX', 'HOU']
}

division_of_team = {team: div for div, teams in al_division.items() for team in teams}

division_long_name = {
  'al_east': 'AL East',
  'al_central': 'AL Central',
  'al_west': 'AL West'
}

team_names = {
  'NYY': 'New York Yankees',
  'TBR': 'Tampa Bay Rays',
  'TOR': 'Toronto Blue Jays',
  'BAL': 'Baltimore Orioles',
  'BOS': 'Boston Red Sox',
  'CHW': 'Chicago White Sox',
  'CLE': 'Cleveland Guardians',
  'DET': 'Detriot Tigers',
  'KCR': 'Kansas City Royals',
  'MIN': 'Minnesota Twins',
  'LAA': 'Los Angeles Angels',
  'OAK': 'Oakland Athletics',
  'SEA': 'Seattle Mariners',
  'TEX': 'Texas Rangers',
  'HOU': 'Houston Astros'
}

# most of these color codes came from 
# https://teamcolorcodes.com/mlb-color-codes/
team_colors = {
  'NYY': '#C4CED3',
  'TBR': '#092C5C',
  'TOR': '#80b0d8',
  'BAL': '#DF4601',
  'BOS': '#BD3039',
  'CHW': '#27251F',
  'CLE': '#E31937',
  'DET': '#0C2340',
  'KCR': '#004687',
  'MIN': '#B9975B',
  'LAA': '#862633',
  'OAK': '#003831',
  'SEA': '#005C5C',
  'TEX': '#003278',
  'HOU': '#EB6E1F'
}

season = pd.date_range(start=datetime(2022, 4, 7), end=datetime(2022, 10, 2))
played_season = pd.to_datetime(pd.date_range(start=datetime(2022, 4, 7), end=pd.Timestamp.today()))

def postseason_race():
  """Generate plotly figure visualizing the postseason race."""
  df = mlb_data(test=False)

  # sort teams by wins over .500
  teams = [(team, df[team].iloc[-1]) for team in df.columns]
  teams.sort(key=lambda x: x[1], reverse=True)
  
  # division leaders
  division_leaders = {}
  for team, wins_over_500 in teams:
      div = division_of_team[team]
      if div not in division_leaders.keys():
        division_leaders[div] = [(team, wins_over_500)]
      elif wins_over_500 == division_leaders[div][0][1]: # tie for first in division
        division_leaders[div].append((team, wins_over_500))

  leaders = [x[0] for div, v in division_leaders.items() for x in v]

  traces = OrderedDict()

  # add line plots of team records
  # offset = np.linspace(-0.1, 0.1, 15)
  # np.random.shuffle(offset)
  for i, (team, _) in enumerate(teams):
      trace_name = team_names[team]
      div = division_of_team[team]
      traces[team] = go.Scatter(
          x=df.index,
          y=df[team], #+ offset[i],
          mode='lines',
          visible=team in al_division['al_east'],
          legendgroup=div,  # this can be any string, not just "group"
          legendgrouptitle_text=division_long_name[div],
          name=trace_name,
          line_color=team_colors[team]
      )

  # # add markers for division leaders
  # for div in al_division.keys():
  #     traces[div] = go.Scatter(
  #         x=[df.index[-1]],
  #         y=[df[leaders[div]].iloc[-1]],
  #         mode='markers',
  #         visible=True,
  #         name=division_long_name[div] + " Leader"
  #     )

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
      args=[{'visible': [True if x not in leaders and x not in al_division.keys() else False for x in traces]}]
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
              buttons=division_buttons + wildcard_button + all_button
          )
      ],
      title=dict(
          text=f'{2022} MLB Postseason Race',
          x=0.1
      ),
      yaxis_title='Wins over .500',
      showlegend=True,
      height=700,
      margin={'r': 300}
  )

  fig = go.Figure(data=list(traces.values()), layout=layout)

  fig.update_xaxes(range=[season.min(), season.max()])
  fig.update_yaxes(range=[df.min().min() - 5, df.max().max() + 5])

  return fig
