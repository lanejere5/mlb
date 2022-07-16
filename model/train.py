# train.py
"""Script for training a model on historical data."""
import urllib.request
import json
import pickle
from datetime import datetime, date, timedelta
from typing import Dict, Tuple, List

from app.elo import ELO


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

def get_game_results(day: date) -> Tuple[List[Dict], List[int]]:
	"""Get game results for given day from MLB statsAPI."""
	url = "https://statsapi.mlb.com/api/v1/schedule?language=en&sportId=1&date="
	url += day.strftime("%m/%d/%Y")

	response = urllib.request.urlopen(url)

	data = json.loads(response.read())

	games = []
	results = []
	for game in data['dates'][0]['games']:
		parsed_game, result = parse_game_results(game)
		if (parsed_game is not None) and (result is not None):
			games.append(parsed_game)
			results.append(result)

	return games, results

if __name__ == '__main__':

	# initialize the model
	params = {
		'rating': 30 * [0],
		'a': 0.0025,
		'b': 0.152,
		'k': 4,
		'map': {
			"ANA": 0,
			"LAA": 0,
			"BAL": 1,
			"BOS": 2,
			"CHA": 3,
			"CHW": 3,
			"CLE": 4,
			"DET": 5,
			"HOU": 6,
			"KCA": 7,
			"KCR": 7,
			"MIN": 8,
			"NYA": 9,
			"NYY": 9,
			"OAK": 10,
			"SEA": 11,
			"TBA": 12,
			"TBR": 12,
			"TEX": 13,
			"TOR": 14,
			"ARI": 15,
			"ATL": 16,
			"CHN": 17,
			"CHC": 17,
			"CIN": 18,
			"COL": 19,
			"LAN": 20,
			"LAD": 20,
			"SDN": 21,
			"SDP": 21,
			"MIA": 22,
			"MIL": 23,
			"NYN": 24,
			"NYM": 24,
			"PHI": 25,
			"PIT": 26,
			"SFN": 27,
			"SFG": 27,
			"SLN": 28,
			"STL": 28,
			"WAS": 29,
			"WSN": 29,
			"MON": 29,
			"CAL": 0,
			"FLO": 22
        },
		"date": "2022-07-12"
	}
	model = ELO(params)

	# start and end dates
	day = datetime(2022, 4, 7).date()
	end_date = date.today() - timedelta(days=2)

	# train the model
	while day <= end_date:
		games, results = get_game_results(day)
		model.train(games, results)
		day += timedelta(days=1)

	pickle.dump(params, open('params.pkl', 'wb'))
