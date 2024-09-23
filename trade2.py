import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objs as go
from alpha_vantage.timeseries import TimeSeries
import datetime

# Alpha Vantage API Key (replace with your own key)
ALPHA_VANTAGE_API_KEY = 'YOUR_API_KEY'

# Define the assets you want to track
assets = {
    'Russell 2000': '^RUT',
    'S&P 500': '^GSPC',
    'VGSH': 'VGSH',
    'Roblox': 'RBLX',
    'SPY': 'SPY',
    'IJR': 'IJR',
    'ONON': 'ONON'
}

# Trade data (updated with ONON)
trades = [
    {'asset': 'Russell 2000', 'date': '2024-08-05', 'action': 'buy'},
    {'asset': 'S&P 500', 'date': '2024-08-05', 'action': 'buy'},
    {'asset': 'VGSH', 'date': '2024-08-05', 'action': 'sell'},
    {'asset': 'Roblox', 'date': '2024-08-13', 'action': 'sell'},
    {'asset': 'Russell 2000', 'date': '2024-08-13', 'action': 'buy'},
    {'asset': 'ONON', 'date': '2024-08-15', 'action': 'sell'},
    {'asset': 'SPY', 'date': '2024-08-26', 'action': 'buy'},
    {'asset': 'Roblox', 'date': '2024-09-05', 'action': 'sell'},
    {'asset': 'IJR', 'date': '2024-09-05', 'action': 'buy'}
]

# Convert trade date strings to datetime objects
for trade in trades:
    trade['date'] = pd.Timestamp(trade['date'])

# Helper function to get dividend yield data
def get_dividends(ticker):
    stock = yf.Ticker(ticker)
    dividends = stock.dividends
    if not dividends.empty:
        dividends = dividends.resample('M').sum()  # Resample by month to avoid high frequency
    return dividends

# Fetch stock data from Alpha Vantage
def get_data_from_alpha_vantage(symbol):
    ts = TimeSeries(key=ALPHA_VANTAGE_API_KEY, output_format='pandas')
    data, meta_data = ts.get_daily(symbol=symbol, outputsize='full')
    return data

# Fetch stock data from yfinance
def get_data_from_yfinance(ticker, start, end):
    return yf.download(ticker, start=start, end=end)

# Streamlit App
st.title("Interactive Trade Tracker with Dividends and Trade Markers")

# Allow user to select asset
selected_asset = st.selectbox('Select an asset:', list(assets.keys()))

# Allow user to pick date range
start_date = st.date_input('Start date', datetime.date(2024, 8, 1))
end_date = st.date_input('End date', datetime.date(2024, 9, 22))

# Choose data source
data_source = st.radio("Choose data source", ("Yahoo Finance", "Alpha Vantage"))

# Fetch data based on the selected data source
if data_source == "Yahoo Finance":
    data = get_data_from_yfinance(assets[selected_asset], start_date, end_date)
else:
    data = get_data_from_alpha_vantage(assets[selected_asset])

# Display Data (Plotly)
fig = go.Figure()

# Plot stock prices
fig.add_trace(go.Scatter(x=data.index, y=data['Adj Close'], mode='lines', name='Price'))

# Plot dividend yield if available
dividends = get_dividends(assets[selected_asset])
if not dividends.empty:
    fig.add_trace(go.Bar(x=dividends.index, y=dividends, name='Dividends', yaxis='y2', marker=dict(color='orange')))

# Add buy/sell markers
for trade in trades:
    if trade['asset'] == selected_asset:
        color = 'green' if trade['action'] == 'buy' else 'red'
        fig.add_vline(x=trade['date'], line_color=color, line_dash="dash")
        fig.add_annotation(x=trade['date'], y=data['Adj Close'].max(), text=f"{trade['action'].capitalize()} {trade['asset']}", showarrow=True, arrowhead=1)

# Customize layout
fig.update_layout(
    title=f"{selected_asset} Prices and Dividends",
    xaxis_title="Date",
    yaxis_title="Price (USD)",
    yaxis2=dict(title="Dividends", overlaying="y", side="right"),
    template='plotly_dark',
    height=600
)

# Display the plot
st.plotly_chart(fig)

# Display a table with trade data
st.subheader(f"Trades for {selected_asset}")
trade_data = pd.DataFrame([trade for trade in trades if trade['asset'] == selected_asset])
st.write(trade_data)

