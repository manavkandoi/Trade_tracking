import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objs as go

# Title
st.title('Interactive Trade Tracker')

# Asset selection
assets = {
    'Russell 2000': '^RUT',
    'S&P 500': '^GSPC',
    'VGSH': 'VGSH',
    'Roblox': 'RBLX',
    'SPY': 'SPY',
    'IJR': 'IJR'
}

selected_asset = st.selectbox('Select an asset:', list(assets.keys()))

# Fetch data
start_date = '2024-08-01'
end_date = '2024-09-22'
ticker = assets[selected_asset]
data = yf.download(ticker, start=start_date, end=end_date)

# Plot data
fig = go.Figure()

# Plot price
fig.add_trace(go.Scatter(x=data.index, y=data['Adj Close'], mode='lines', name='Price'))

# Show plot
st.plotly_chart(fig)
