# visualize.py
"""Generate plotly figure visualizing the postseason race."""
from datetime import datetime, timedelta
from collections import OrderedDict
from typing import List, Dict

import plotly.graph_objects as go

import load


def generate_traces(teams: Dict) -> OrderedDict[go.Scatter]:
  """Generate traces for the plot.

  Args:
    teams: Team data.

  Returns:
    OrderedDict of plotly Scatter objects.
  """
  traces = OrderedDict()

  # add line plots of team records
  # teams are added in descending order so they will 
  # appear according to their rank in the legend
  for team, data in sorted(teams.items(), key=lambda x: x[1]['rank']):
    trace_name = data['name'] + ' (' + str(data['wins']) + '-' + str(data['losses']) + ')'
    dates = [datetime(2022, 4, 7) + timedelta(days=i) for i in range(len(data['record']))]
    traces[team] = go.Scatter(
      x=dates,
      y=data['record'],
      mode='lines',
      visible=(data['div'] == 'AL East'),
      legendgroup=data['div'],
      legendgrouptitle_text=data['div'],
      name=trace_name,
      line_color=data['color']
    )
  return traces

def generate_buttons(traces: OrderedDict[go.Scatter], teams: Dict) -> List:
  """Generate buttons for dropdown menu.

  Args:
    traces: Traces to be plotted.
    teams: Team data.

  Returns:
    List of buttons, in the order they appear in the menu.
  """

  buttons = []

  # american league buttons

  # al division buttons
  al_divisions = ['AL East', 'AL Central', 'AL West']
  buttons += [
    dict(
      method='update',
      label=div,
      visible=True,
      args=[{'visible': [True if x['legendgroup'] == div else False for x in traces.values()] }]
    )
    for div in al_divisions
  ]

  # al wildcard button
  al_wildcard_flags = [
    True if teams[team]['rank'] > 1 and teams[team]['league'] == 'American League (AL)' else False for team in traces.keys()
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
    True if teams[team]['league'] == 'American League (AL)' else False for team in traces.keys()
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
  nl_divisions = ['NL East', 'NL Central', 'NL West']
  buttons += [
    dict(
      method='update',
      label=div,
      visible=True,
      args=[{'visible': [True if x['legendgroup'] == div else False for x in traces.values()] }]
    )
    for div in nl_divisions
  ]

  # nl wildcard button
  nl_wildcard_flags = [
    True if teams[team]['rank'] > 1 and teams[team]['league'] == 'National League (NL)' else False for team in traces.keys()
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
    True if x['legendgroup'][:2] == 'NL' else False for x in traces.values()
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
  dashboard_data = load.dashboard_data(test=False)
  traces = generate_traces(dashboard_data['teams'])
  buttons = generate_buttons(traces, dashboard_data['teams'])

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

  # fix the axis ranges so that selecting buttons doesn't shift things around
  fig.update_xaxes(range=[datetime(2022, 4, 7), datetime(2022, 10, 2)])

  y_min = min([min(data['record']) for data in dashboard_data['teams'].values()])
  y_max = max([max(data['record']) for data in dashboard_data['teams'].values()])
  fig.update_yaxes(range=[y_min - 2, y_max + 2])

  return fig
