# visualize.py
"""Generate plotly figure visualizing the postseason race."""
from datetime import datetime, timedelta
from collections import OrderedDict
from typing import OrderedDict as OrderedDictType
from typing import List, Dict, Tuple
from copy import copy

import plotly.graph_objects as go


ScatterDict = OrderedDictType[str, go.Scatter]

def generate_traces(teams: Dict[str, Dict]) -> ScatterDict:
  """Generate traces for the plot.

  Args:
  -----
    teams: Dict of data for each team.
      
      Keys: team abbr (e.g., 'TOR'). 
      Values: Dicts containing keys:
        'name': full team name, e.g., 'New York Yankees'
        'league': e.g., 'American League (AL)'
        'div': e.g., 'AL East'
        'color': html code for the team colour, e.g., '#C4CED3'
        'record': List[int] containing the wins over 500 for each day
          in the season so far. This is what is plotted. Length is number
          of days elapsed in the season to date.
        'wins': int, total wins.
        'losses': int, total losses.
        'rank': int, rank within division according to FanGraphs.
          Ties are possible.
        'forecast' (optional): List[int] containing wins over 500 for a
          given number of days beyond the current day.

  Returns:
  --------
    OrderedDict of plotly Scatter objects.
      
      Keys: team abbr. 
      Values: go.Scatter object.
      
      Dict is ordered according to 'rank' so that teams are listed by
      rank in the legend.
  """
  traces = OrderedDict()

  # add line plots of team records
  # teams are sorted by rank so that legend is ordered
  for team, data in sorted(teams.items(), key=lambda x: x[1]['rank']):
    trace_name = f"{data['name']} ({str(data['wins'])}-{str(data['losses'])})"
    
    # x-axis and y=-axis values for the plot
    y_vals = copy(data['record'])
    if 'forecast' in data:
       y_vals += data['forecast']
    x_vals = [
      datetime(2022, 4, 7) + timedelta(days=i) for i in range(len(y_vals))
    ]

    traces[team] = go.Scatter(
      x=x_vals,
      y=y_vals,
      mode='lines',
      visible=(data['div'] == 'AL East'), # only AL East visible on page load
      legendgroup=data['div'],
      legendgrouptitle_text=data['div'],
      name=trace_name,
      line_color=data['color']
    )

  return traces

def generate_buttons(traces: ScatterDict, teams: Dict[str, Dict]) -> List[Dict]:
  """Generate buttons for dropdown menu.

  Args:
  -----
    traces: Traces to be plotted. See generate_traces().
    teams: Team data. See generate_traces().

  Returns:
  --------
    List of button dicts in the order they appear in the menu.
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

def postseason_race(dashboard_data: Dict=None) -> Tuple[go.Figure, datetime]:
  """Generate plotly figure visualizing the 2022 postseason race.

  Args:
  -----
    dashboard_data (optional): pass dashboard data directly instead of loading
      from bucket. For testing purposes.

  Returns:
  --------
    plotly figure.
    datetime that the data was collected.
  """
  if dashboard_data is None:
    import load
    dashboard_data = load.dashboard_data()

  date_created = datetime.strptime(dashboard_data['created'], "%Y-%m-%d")

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

  # fix axis ranges so that selecting buttons doesn't shift things around
  fig.update_xaxes(range=[datetime(2022, 4, 7), datetime(2022, 10, 2)])

  y_min = min([min(trace['y']) for trace in traces.values()]) - 2
  y_max = max([max(trace['y']) for trace in traces.values()]) + 2

  fig.update_yaxes(range=[y_min, y_max])

  if 'forecast' in dashboard_data['teams']['TOR']:
    forcast_length = len(dashboard_data['teams']['TOR']['forecast'])

    record_end = date_created - timedelta(days=1)
    fig.add_vline(
        x=record_end,
        line_width=1.5,
        line_dash="dash",
        line_color="grey"
    )
    fig.add_vrect(
        x0=record_end,
        x1=record_end + timedelta(days=forcast_length),
        line_width=0,
        fillcolor="grey",
        opacity=0.2
    )

  return fig, date_created
