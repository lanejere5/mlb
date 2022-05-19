# main.py
"""Dashboard entry point."""
from dash import Dash, html, dcc
from flask import Flask
from visualize import postseason_race

description = '''
  Created by [Jeremy Lane](https://github.com/lanej5). [View source on github](https://github.com/lanej5/mlb). Data is updated daily around 10AM ET.   
'''

server = Flask(__name__)

app = Dash(__name__, server=server)
app.title = 'Postseason Race'
app.layout = html.Div(children=[
  dcc.Graph(
    id='postseason_race',
    figure=postseason_race()
  ),
  dcc.Markdown(children=description)
])

if __name__ == '__main__':
  app.run_server(debug=True)
