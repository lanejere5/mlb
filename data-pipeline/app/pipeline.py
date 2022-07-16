# pipeline.py
"""Data pipeline."""
import urllib
import json
import os
from dotenv import load_dotenv
from datetime import datetime, date, timedelta
from typing import List, Dict, Tuple
from collections import defaultdict

from google.cloud import storage

from model_interface import train, forecast


# gross, put this in a config file
divisions = {
  'al_east': ['NYY', 'TBR', 'TOR', 'BAL', 'BOS'],
  'al_central': ['CHW', 'CLE', 'DET', 'KCR', 'MIN'],
  'al_west': ['LAA', 'OAK', 'SEA', 'TEX', 'HOU'],
  'nl_east': ['ATL', 'NYM', 'PHI', 'MIA', 'WSN'],
  'nl_central': ['CHC', 'MIL', 'STL', 'PIT', 'CIN'],
  'nl_west': ['LAD', 'COL', 'ARI', 'SFG', 'SDP']
}

teams = [team for div, teams in divisions.items() for team in teams]

team_div = {
  team: div for div, teams in divisions.items() for team in teams
}

team_name_abbr = {
  'New York Yankees': 'NYY',
  'Tampa Bay Rays': 'TBR',
  'Toronto Blue Jays': 'TOR',
  'Baltimore Orioles': 'BAL',
  'Boston Red Sox': 'BOS',
  'Chicago White Sox': 'CHW',
  'Cleveland Guardians': 'CLE',
  'Detroit Tigers': 'DET',
  'Kansas City Royals': 'KCR',
  'Minnesota Twins': 'MIN',
  'Los Angeles Angels': 'LAA',
  'Oakland Athletics': 'OAK',
  'Seattle Mariners': 'SEA',
  'Texas Rangers': 'TEX',
  'Houston Astros': 'HOU',
  'Atlanta Braves': 'ATL',
  'New York Mets': 'NYM',
  'Philadelphia Phillies': 'PHI',
  'Miami Marlins': 'MIA',
  'Washington Nationals': 'WSN',
  'Chicago Cubs': 'CHC',
  'Milwaukee Brewers': 'MIL',
  'St. Louis Cardinals': 'STL',
  'Pittsburgh Pirates': 'PIT',
  'Cincinnati Reds': 'CIN',
  'Los Angeles Dodgers': 'LAD',
  'Colorado Rockies': 'COL',
  'Arizona Diamondbacks': 'ARI',
  'San Francisco Giants': 'SFG',
  'San Diego Padres': 'SDP'
}

class Pipeline():
  """Pipeline class.

  This "class" simply encapsulates a pipeline that implements
  the following sequence of operations. The pipeline is invoked by
  run().
  """
  def __init__(self):
    # base url for statsapi calls
    self.statsAPI_base_url = "https://statsapi.mlb.com"

    # bucket for dashboard data
    load_dotenv()
    storage_client = storage.Client()
    bucket = storage_client.bucket(os.environ.get('MLB-DATA-BUCKET-NAME'))
    self.blob = bucket.blob(str(date.today()) + '-dashboard-data.json')

  @staticmethod
  def parse_game_results(game: Dict) -> Tuple[Dict, int]:
    """Parse data from MLB statsapi.

    Returns:
    --------
    parsed_game: selected fields from statsAPI data
    result: 1 if home team won, 0 if home team lost, None if game was not played
    """
    home_name = game['teams']['home']['team']['name']
    visitor_name = game['teams']['away']['team']['name']
    if (home_name in team_name_abbr) and (visitor_name in team_name_abbr):
      parsed_game = {
        'home': team_name_abbr[home_name],
        'visitor': team_name_abbr[visitor_name],
        'date': game['officialDate']
      }
    else:
      parsed_game = None

    if 'isWinner' in game['teams']['home']:
      result = int(game['teams']['home']['isWinner'])
    else:
      result = None
    return parsed_game, result

  def get_game_results(self, day: date) -> Tuple[List[Dict], List[int]]:
    """Get game results for given day from MLB statsAPI."""
    url = self.statsAPI_base_url + "/api/v1/schedule?language=en&sportId=1&date="
    url += day.strftime("%m/%d/%Y")

    response = urllib.request.urlopen(url)

    data = json.loads(response.read())

    games = []
    results = []
    for game in data['dates'][0]['games']:
      parsed_game, result = self.parse_game_results(game)
      if (parsed_game is not None) and (result is not None):
        games.append(parsed_game)
        results.append(result)

    return games, results

  def train_models(self,
                   model_names: List[str],
                   games: List[Dict],
                   results: List[int]) -> None:
    """Train models from game data."""
    for model_name in model_names:
      train(model_name, games, results)

  @staticmethod
  def parse_future_game(game: Dict) -> Dict:
    """Parse future game from statsAPI."""
    home_name = game['teams']['home']['team']['name']
    visitor_name = game['teams']['away']['team']['name']
    if (home_name in team_name_abbr) and (visitor_name in team_name_abbr):
      parsed_future_game = {
        'home': team_name_abbr[home_name],
        'visitor': team_name_abbr[visitor_name],
        'date': game['officialDate']
      }
    else:
      parsed_future_game = None
    return parsed_future_game


  def get_schedule(self, start_date: date, end_date: date) -> List[Dict]:
    """Get schedule for date range (inclusive)."""
    url = self.statsAPI_base_url + "/api/v1/schedule?language=en&sportId=1"
    url += "&startDate=" + start_date.strftime("%m/%d/%Y")
    url += "&endDate=" + end_date.strftime("%m/%d/%Y")
    response = urllib.request.urlopen(url)
    data = json.loads(response.read())

    games = []

    for day in data['dates']:
      for game in day['games']:
        parsed_future_game = self.parse_future_game(game)
        if parsed_future_game is not None:
          games.append(parsed_future_game)

    return games

  def get_dashboard_data(self) -> Dict:
    """Retrieve dashboard data from bucket."""
    return json.loads(self.blob.download_as_string())

  def put_dashboard_data(self, dashboard_data: Dict) -> None:
    """Put dashboard data in bucket."""
    self.blob.upload_from_string(json.dumps(dashboard_data))

  def update_dashboard(self,
                       games: List[Dict],
                       results: List[int],
                       schedule: List[Dict],
                       forecast_results: List[float]) -> None:
    """Update dashboard data with game results and forecast."""
    # collect results by team
    team_results = defaultdict(int)
    for game, result in zip(games, results):
      team_results[game['home']] += 2 * result - 1
      team_results[game['visitor']] += 1 - 2 * result

    # load dashboard data
    dashboard_data = self.get_dashboard_data()

    # update team records, win / loss, and rank
    div_leader = {div: -10e5 for div, _ in divisions.items()}
    num_days = (date.today() - date(2022, 4, 7)).days # number of days in season so far
    for team in teams:
      if len(dashboard_data['teams'][team]['record']) == num_days - 1:
        dashboard_data['teams'][team]['record'].append(
          dashboard_data['teams'][team]['record'][-1] + team_results[team]
        )
        if team_results[team] > 0:
          dashboard_data['teams'][team]['wins'] += team_results[team]
        else:
          dashboard_data['teams'][team]['losses'] -= team_results[team]

      elif len(dashboard_data['teams'][team]['record']) < num_days - 1:
        print(f"Error: Record of {team} is missing days.")

      # compute wins over 500 and update division leader
      dashboard_data['teams'][team]['wins_over_500'] = dashboard_data['teams'][team]['wins'] - dashboard_data['teams'][team]['losses']
      if dashboard_data['teams'][team]['wins_over_500'] > div_leader[team_div[team]]:
        div_leader[team_div[team]] = dashboard_data['teams'][team]['wins_over_500']

    # compute games back
    for team in teams:
      dashboard_data['teams'][team]['gb'] = (div_leader[team_div[team]] - dashboard_data['teams'][team]['wins_over_500']) / 2
    
    # rank divisions
    def dense_rank(l: List[int]) -> List[int]:
      # Dense rank non-increasing list of integers.
      # Assumes l is sorted in decreasing order.
      if not l:
        return l
      ranks = [1]
      for i in range(1, len(l)):
        if l[i] == l[i - 1]:
          ranks.append(ranks[-1])
        else:
          ranks.append(ranks[-1] + 1)
      return ranks
    
    def rank_division(team_list: List[Tuple[str, int]]):
      # Rank division
      # Args: Each item in the list is a pair x = ('TOR', 5)
      # where x[1] is the number of games back
      # Returns: pairs x = ('TOR', 3) where x[1] is division rank
      team_list.sort(key=lambda x: x[1], reverse=False)
      gb = [x[1] for x in team_list]
      return [(x[0], rank) for (x, rank) in zip(team_list, dense_rank(gb))]

    for div, ts in divisions.items():
      team_list = [(t, dashboard_data['teams'][t]['gb']) for t in ts]
      print(team_list)
      team_ranks = rank_division(team_list)
      print(team_ranks)
      for x in team_ranks:
        dashboard_data['teams'][x[0]]['rank'] = x[1]

    # collect forecasted results by date and team
    forecast_team_results = defaultdict(float)
    for game, prob in zip(schedule, forecast_results):
      d = datetime.strptime(game['date'], '%Y-%m-%d').date()
      forecast_team_results[(d, game['home'])] += 2 * prob - 1
      forecast_team_results[(d, game['visitor'])] += 1 - 2 * prob
        
    # convert game forecasts to wins over 500 for each team
    for team in teams:
      dashboard_data['teams'][team]['forecast'] = []
    dates = [date.today() + timedelta(days=i) for i in range(30)] # poor cohesion here
    for d in dates:
      for team in teams:
        if len(dashboard_data['teams'][team]['forecast']) == 0:
          x = dashboard_data['teams'][team]['record'][-1] + forecast_team_results[(d, team)]
          dashboard_data['teams'][team]['forecast'].append(x)
        else:
          x = dashboard_data['teams'][team]['forecast'][-1] + forecast_team_results[(d, team)]
          dashboard_data['teams'][team]['forecast'].append(x)

    # update date
    dashboard_data['created'] = datetime.today().strftime('%Y-%m-%d')

    self.put_dashboard_data(dashboard_data)
  
  def run(self) -> int:
    """Run data pipeline.

    1. Get game results for previous day from MLB statsapi.
    2. Train model(s) using game results (1). Depending on the model
       this may require gathering additional data.
    3. Get upcoming schedule from MLB statsAPI.
    4. Get forecast from model using schedule from (3).
    5. Load the dashboard data file from bucket
    6. Update dashboard data with results (1) and forecast (4).
    7. Put updated dashboard data file back into bucket.
    """
    season_end = date(2022, 10, 2)
    if date.today() > season_end:
      return
    # 1. get results of yesterday's games
    print("Retrieving game results...")
    games, results = self.get_game_results(date.today() - timedelta(days=1))

    # 2. train the models
    print("Training models...")
    model_names = ['elo']
    self.train_models(model_names, games, results)

    # 3 - 4. forecast next 30 days
    print("Retrieving schedule...")
    end_date = min(date.today() + timedelta(days=30), season_end)
    schedule = self.get_schedule(date.today(), end_date)
    model_name = 'elo'
    print("Retrieving forecast...")
    forecast_results = forecast(model_name, schedule)

    # 5 - 7. update dashboard data
    print("Updating dashboard...")
    self.update_dashboard(games, results, schedule, forecast_results)

    return 200
    