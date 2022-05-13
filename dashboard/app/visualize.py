# visualize.py
"""Generate plotly figure visualizing the postseason race."""
import numpy as np
from datetime import datetime
from collections import OrderedDict

import plotly.graph_objects as go
from pandas import date_range, to_datetime, Timestamp

from load import mlb_data


divisions = {
  'al_east': ['NYY', 'TBR', 'TOR', 'BAL', 'BOS'],
  'al_central': ['CHW', 'CLE', 'DET', 'KCR', 'MIN'],
  'al_west': ['LAA', 'OAK', 'SEA', 'TEX', 'HOU'],
  'nl_east': ['ATL', 'NYM', 'PHI', 'MIA', 'WSN'],
  'nl_central': ['CHC', 'MIL', 'STL', 'PIT', 'CIN'],
  'nl_west': ['LAD', 'COL', 'ARI', 'SFG', 'SDP']
}

division_of_team = {team: div for div, teams in divisions.items() for team in teams}

league_of_division = {
  'al_east': 'al',
  'al_central': 'al',
  'al_west': 'al',
  'nl_east': 'nl',
  'nl_central': 'nl',
  'nl_west': 'nl'
}

division_long_name = {
  'al_east': 'AL East',
  'al_central': 'AL Central',
  'al_west': 'AL West',
  'nl_east': 'NL East',
  'nl_central': 'NL Central',
  'nl_west': 'NL West'
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
  'HOU': 'Houston Astros',
  'ATL': 'Atlanta Braves',
  'NYM': 'New York Mets',
  'PHI': 'Philadelphia Phillies',
  'MIA': 'Miami Marlins',
  'WSN': 'Washington Nationals',
  'CHC': 'Chicago Cubs',
  'MIL': 'Milwaukee Brewers',
  'STL': 'St. Louis Cardinals',
  'PIT': 'Pittsburgh Pirates',
  'CIN': 'Cincinnati Reds',
  'LAD': 'Los Angeles Dodgers',
  'COL': 'Colorado Rockies',
  'ARI': 'Arizona Diamondbacks',
  'SFG': 'San Francisco Giants',
  'SDP': 'San Diego Padres'
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
  'HOU': '#EB6E1F',
  'ATL': '#CE1141',
  'NYM': '#FF5910',
  'PHI': '#E81828',
  'MIA': '#00A3E0',
  'WSN': '#AB0003',
  'CHC': '#0E3386',
  'MIL': '#ffc52f',
  'STL': '#FEDB00',
  'PIT': '#27251F',
  'CIN': '#C6011F',
  'LAD': '#005A9C',
  'COL': '#33006F',
  'ARI': '#E3D4AD',
  'SFG': '#27251F',
  'SDP': '#2F241D'
}

season = date_range(start=datetime(2022, 4, 7), end=datetime(2022, 10, 2))
played_season = to_datetime(date_range(start=datetime(2022, 4, 7), end=Timestamp.today()))

def postseason_race() -> go.Figure:
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
          visible=team in divisions['al_east'],
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

  # al button
  al_button = [
      dict(
          method='update',
          label='American League (AL)',
          visible=True,
          args=[{'visible': [True if league_of_division[division_of_team[x]] == 'al' else False for x in traces]}]
      )
  ]

  # nl button
  nl_button = [
      dict(
          method='update',
          label='American League (AL)',
          visible=True,
          args=[{'visible': [True if league_of_division[division_of_team[x]] == 'nl' else False for x in traces]}]
      )
  ]

  # division buttons
  al_division_buttons = [
      dict(
          method='update',
          label=division_long_name[div],
          visible=True,
          args=[{'visible': [True if x in divisions[div] else False for x in traces] }]
      )
      for div in divisions if league_of_division[div] == 'al'
  ]
  nl_division_buttons = [
      dict(
          method='update',
          label=division_long_name[div],
          visible=True,
          args=[{'visible': [True if x in divisions[div] else False for x in traces] }]
      )
      for div in divisions if league_of_division[div] == 'nl'
  ]

  # wildcard button
  al_wildcard_button = [dict(
      method='restyle',
      label='AL Wildcard',
      visible=True,
      args=[{'visible': [True if x not in leaders and league_of_division[division_of_team[x]] == 'al' else False for x in traces]}]
  )]
  nl_wildcard_button = [dict(
      method='restyle',
      label='NL Wildcard',
      visible=True,
      args=[{'visible': [True if x not in leaders and league_of_division[division_of_team[x]] == 'nl' else False for x in traces]}]
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
              buttons=al_division_buttons + al_wildcard_button + al_button + nl_division_buttons + nl_wildcard_button + nl_button
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
