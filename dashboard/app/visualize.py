# visualize.py
"""Generate plotly figure visualizing the postseason race."""
from datetime import datetime
from collections import OrderedDict
from typing import List, Tuple

import plotly.graph_objects as go

import load


teams_data = load.teams()


def sort_teams_by_record(records) -> List[Tuple[str, int]]:
  """Sort teams in descending order by current wins over 500.

  Args:
    records: pd.DataFrame.

  Returns:
    List of tuples (x, y) where x is the team abbreviation and y is 
    the teams current wins over 500.
  """
  sorted_teams = [(team, records[team].iloc[-1]) for team in records.columns]
  sorted_teams.sort(key=lambda x: x[1], reverse=True)
  return sorted_teams

def generate_traces(sorted_teams, records):
  """Generate traces for the plot."""
  traces = OrderedDict()

  # add line plots of team records
  # teams are added in descending order so they will 
  # appear according to their rank in the legend
  for i, (team, _) in enumerate(sorted_teams):
    trace_name = teams_data['team_names'][team]
    div = teams_data['division_of_team'][team]
    traces[team] = go.Scatter(
      x=records.index,
      y=records[team],
      mode='lines',
      visible=team in teams_data['divisions']['al_east'],
      legendgroup=div,
      legendgrouptitle_text=teams_data['division_long_name'][div],
      name=trace_name,
      line_color=teams_data['team_colors'][team]
    )
  return traces

def get_division_leaders(sorted_teams: List[Tuple[str, int]]):
  # division leaders
  division_leaders = {}
  for team, wins_over_500 in sorted_teams:
      div = teams_data['division_of_team'][team]
      if div not in division_leaders.keys():
        division_leaders[div] = [(team, wins_over_500)]
      elif wins_over_500 == division_leaders[div][0][1]: # tie for first in division
        division_leaders[div].append((team, wins_over_500))

  return [x[0] for div, v in division_leaders.items() for x in v]

def generate_buttons(traces: OrderedDict, leaders: List) -> List:
  """Generate buttons for dropdown menu.

  Returns:
    List of buttons, in the order they appear in the menu.
  """
  buttons = []

  # american league buttons

  # al division buttons
  buttons += [
    dict(
      method='update',
      label=teams_data['division_long_name'][div],
      visible=True,
      args=[{'visible': [True if x in teams_data['divisions'][div] else False for x in traces] }]
    )
    for div in teams_data['divisions'] if teams_data['league_of_division'][div] == 'al'
  ]

  # al wildcard button
  al_wildcard_flags = [
    True if x not in leaders and teams_data['league_of_division'][teams_data['division_of_team'][x]] == 'al' else False for x in traces
  ]
  buttons.append(
    dict(
      method='restyle',
      label='AL Wildcard',
      visible=True,
      args=[{'visible': al_wildcard_flags}]
    )
  )

  # al league button
  al_flags = [
    True if teams_data['league_of_division'][teams_data['division_of_team'][x]] == 'al' else False for x in traces
  ]
  buttons.append(
    dict(
      method='update',
      label='American League (AL)',
      visible=True,
      args=[{'visible': al_flags}]
    )
  )

  # national league buttons

  # nl division buttons
  buttons += [
    dict(
      method='update',
      label=teams_data['division_long_name'][div],
      visible=True,
      args=[{'visible': [True if x in teams_data['divisions'][div] else False for x in traces] }]
    )
    for div in teams_data['divisions'] if teams_data['league_of_division'][div] == 'nl'
  ]

  # nl wildcard button
  nl_wildcard_flags = [
    [True if x not in leaders and teams_data['league_of_division'][teams_data['division_of_team'][x]] == 'nl' else False for x in traces]
  ]
  buttons.append(
    dict(
      method='restyle',
      label='NL Wildcard',
      visible=True,
      args=[{'visible': nl_wildcard_flags}]
    )
  )

  # nl league button
  nl_flags = [
    True if teams_data['league_of_division'][teams_data['division_of_team'][x]] == 'nl' else False for x in traces
  ]
  buttons.append(
    dict(
      method='update',
      label='National League (NL)',
      visible=True,
      args=[{'visible': nl_flags}]
    )
  )

  return buttons

def postseason_race() -> go.Figure:
  """Generate plotly figure visualizing the 2022 postseason race.

  Returns:
    A plotly figure.
  """
  # load records
  records = load.records(test=True)

  # sort teams by wins over .500
  sorted_teams = sort_teams_by_record(records)
  leaders = get_division_leaders(sorted_teams)
  traces = generate_traces(sorted_teams, records)
  buttons = generate_buttons(traces, leaders)

  # create the layout 
  layout = go.Layout(
    updatemenus=[
      dict(
        type='dropdown',
        direction='down',
        x=1,
        y=1.15,
        showactive=True,
        buttons=buttons
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

  # fix the axis ranges so that selecting buttons doesn't shift them
  fig.update_xaxes(range=[datetime(2022, 4, 7), datetime(2022, 10, 2)])
  fig.update_yaxes(range=[records.min().min() - 2, records.max().max() + 2])

  return fig
