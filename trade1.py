import dash
from dash import dcc, html
import dash_core_components as dcc
import dash_html_components as html
import yfinance as yf
import pandas as pd
import plotly.graph_objs as go

# Define the app
app = dash.Dash(__name__)

# Fetch stock data
def get_stock_data(ticker, start, end):
    return yf.download(ticker, start=start, end=end)

# Define assets and trades
assets = {
    'Russell 2000': '^RUT',
    'S&P 500': '^GSPC',
    'VGSH': 'VGSH',
    'Roblox': 'RBLX',
    'SPY': 'SPY',
    'IJR': 'IJR'
}

trades = [
    {'asset': 'Russell 2000', 'date': '2024-08-05', 'action': 'buy'},
    {'asset': 'S&P 500', 'date': '2024-08-05', 'action': 'buy'},
    {'asset': 'VGSH', 'date': '2024-08-05', 'action': 'sell'},
]

# Layout
app.layout = html.Div([
    dcc.Dropdown(
        id='asset-dropdown',
        options=[{'label': asset, 'value': asset} for asset in assets],
        value='Russell 2000'
    ),
    dcc.Graph(id='price-graph'),
])

# Update graph callback
@app.callback(
    dash.dependencies.Output('price-graph', 'figure'),
    [dash.dependencies.Input('asset-dropdown', 'value')]
)
def update_graph(selected_asset):
    start_date = '2024-08-01'
    end_date = '2024-09-22'
    
    # Fetch data
    ticker = assets[selected_asset]
    data = get_stock_data(ticker, start_date, end_date)

    # Create figure
    fig = go.Figure()

    # Plot stock price
    fig.add_trace(go.Scatter(x=data.index, y=data['Adj Close'], mode='lines', name='Price'))

    # Add buy/sell markers
    for trade in trades:
        if trade['asset'] == selected_asset:
            color = 'green' if trade['action'] == 'buy' else 'red'
            fig.add_vline(x=trade['date'], line_color=color, line_dash="dash")

    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
