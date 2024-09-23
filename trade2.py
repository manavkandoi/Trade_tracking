#linked to github for teh webapp that shows the trades and potentia/realized gains

import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objs as go
import datetime

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

# Trade data including the buy/sell amounts
trades = [
    {'asset': 'Russell 2000', 'date': '2024-08-05', 'action': 'buy', 'amount_usd': 700_000},
    {'asset': 'S&P 500', 'date': '2024-08-05', 'action': 'buy', 'amount_usd': 2_997_800},
    {'asset': 'VGSH', 'date': '2024-08-05', 'action': 'sell', 'amount_usd': 325_007},
    {'asset': 'Roblox', 'date': '2024-08-13', 'action': 'sell', 'amount_usd': 234_000},
    {'asset': 'Russell 2000', 'date': '2024-08-13', 'action': 'buy', 'amount_usd': 325_000},
    {'asset': 'ONON', 'date': '2024-08-15', 'action': 'sell', 'amount_usd': 153_000},
    {'asset': 'SPY', 'date': '2024-08-26', 'action': 'buy', 'amount_usd': 151_000},
    {'asset': 'Roblox', 'date': '2024-09-05', 'action': 'sell', 'amount_usd': 215_000},
    {'asset': 'IJR', 'date': '2024-09-05', 'action': 'buy', 'amount_usd': 215_000}
]

# Convert trade date strings to datetime objects
for trade in trades:
    trade['date'] = pd.Timestamp(trade['date'])

# Helper function to get dividend yield data
def get_dividends(ticker):
    stock = yf.Ticker(ticker)
    dividends = stock.dividends
    return dividends

# Fetch stock data from yfinance
def get_data_from_yfinance(ticker, start, end):
    return yf.download(ticker, start=start, end=end)

# Function to calculate profit or loss
def calculate_profit_or_loss(trade, current_price):
    number_of_shares = trade['amount_usd'] / trade['price']  # Calculate shares based on trade price
    if trade['action'] == 'buy':
        return (current_price - trade['price']) * number_of_shares
    else:
        # Realized profit/loss for sell transaction
        return (trade['price'] - current_price) * number_of_shares

# Streamlit App
st.title("Interactive Trade Tracker with Dividends, Trade Markers, and Profit/Loss Calculations")

# Allow user to select asset
selected_asset = st.selectbox('Select an asset:', list(assets.keys()))

# Allow user to pick date range (limit to the trade dates)
start_date = st.date_input('Start date', datetime.date(2024, 8, 1))
end_date = st.date_input('End date', datetime.date(2024, 9, 22))

# Toggle between Candlestick and Line Chart
use_candlestick = st.checkbox('Show Candlestick Chart')

# Toggle between raw price and percentage changes
show_percentage_changes = st.checkbox('Show Percentage Changes')

# Toggle to show dividends
show_dividends = st.checkbox('Show Dividends')

# Toggle between showing dividends as a table or a graph
show_dividends_as_table = st.checkbox('Show Dividends as Table (Uncheck for Graph)')

# Fetch data
data = get_data_from_yfinance(assets[selected_asset], start_date, end_date)

# **Limit the date range based on user input**
data = data[(data.index >= str(start_date)) & (data.index <= str(end_date))]

# Calculate percentage changes if the checkbox is selected
if show_percentage_changes:
    data['Adj Close'] = data['Adj Close'].pct_change() * 100  # Convert to percentage changes

# Get the latest price for profit/loss calculation
latest_price = data['Adj Close'].iloc[-1]

# Display Data (Plotly)
fig = go.Figure()

# Plot stock prices
if use_candlestick:
    fig.add_trace(go.Candlestick(x=data.index,
                                 open=data['Open'],
                                 high=data['High'],
                                 low=data['Low'],
                                 close=data['Adj Close'],
                                 name='Price',
                                 increasing_line_color='green', decreasing_line_color='red'))
else:
    fig.add_trace(go.Scatter(x=data.index, y=data['Adj Close'], mode='lines', name='Price', line=dict(color='blue')))

# Add buy/sell markers and handle missing data gracefully
for trade in trades:
    if trade['asset'] == selected_asset:
        try:
            # Get trade price
            trade_price = data.loc[data.index == trade['date'], 'Adj Close'].values[0]
        except IndexError:
            st.warning(f"Data not available for trade date: {trade['date'].strftime('%Y-%m-%d')}. Skipping trade.")
            continue

        trade['price'] = trade_price  # Save trade price for later
        
        color = 'green' if trade['action'] == 'buy' else 'red'
        fig.add_vline(x=trade['date'], line_color=color, line_dash="dash")
        fig.add_annotation(x=trade['date'], y=data['Adj Close'].max(), text=f"{trade['action'].capitalize()} {trade['asset']}", showarrow=True, arrowhead=1)

# **Customize layout for stock prices**
fig.update_layout(
    title=f"{selected_asset} Prices and Dividends",
    xaxis_title="Date",
    yaxis_title="Price (USD)" if not show_percentage_changes else "Percentage Change (%)",
    template='plotly_white',
    height=600
)

# Display the stock price plot
st.plotly_chart(fig)

# Profit and Loss Calculation for the selected asset
st.subheader(f"Profit/Loss Summary for {selected_asset}")
profit_loss_summary = []

# Calculate profit or loss for each trade
for trade in trades:
    if trade['asset'] == selected_asset:
        try:
            # Calculate profit or loss
            profit_or_loss = calculate_profit_or_loss(trade, latest_price)
            trade_type = "Potential" if trade['action'] == 'buy' else "Realized"
            profit_loss_summary.append({
                'Trade Date': trade['date'].strftime('%Y-%m-%d'),
                'Action': trade['action'].capitalize(),
                'Amount (USD)': trade['amount_usd'],
                'Trade Price': trade['price'],
                'Current/Close Price': latest_price,
                'Profit/Loss (USD)': profit_or_loss,
                'Type': trade_type
            })
        except KeyError:
            st.warning(f"Skipping trade for {selected_asset} due to missing data.")

# Display profit/loss summary as a table
profit_loss_df = pd.DataFrame(profit_loss_summary)
st.write(profit_loss_df)

# Show dividends section if checkbox is selected
if show_dividends:
    st.subheader(f"Dividends for {selected_asset}")
    dividends = get_dividends(assets[selected_asset])
    
    if not dividends.empty:
        # Normalize both the start_date and dividends index to remove timezone differences
        start_date_normalized = pd.Timestamp(start_date).tz_localize(None)
        dividends.index = dividends.index.tz_localize(None)

        # Filter dividends from the start date
        dividends = dividends[dividends.index >= start_date_normalized]

        if show_dividends_as_table:
            # Display dividends as a table
            st.write(dividends)
        else:
            # Display dividends as a graph
            div_fig = go.Figure(go.Bar(x=dividends.index, y=dividends, name='Dividends', marker=dict(color='orange')))
            div_fig.update_layout(
                title=f"{selected_asset} Dividends",
                xaxis_title="Date",
                yaxis_title="Dividends (USD)",
                template='plotly_white',
                height=400
            )
            st.plotly_chart(div_fig)
    else:
        st.warning(f"No dividends available for {selected_asset} in the selected date range.")
