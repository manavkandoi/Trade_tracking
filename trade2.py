import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objs as go
from prophet import Prophet
import datetime

# =============================== Section 1: S&P 500 Indicator Prediction ===============================

# Define the S&P 500 ticker symbol
ticker = '^GSPC'

# Fetch stock data from yfinance for the past 15 years
def get_data_from_yfinance(ticker):
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=365 * 15)
    data = yf.download(ticker, start=start_date, end=end_date)
    return data

# Function to calculate RSI
def calculate_rsi(data, window=14):
    delta = data['Adj Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# Function to calculate MACD
def calculate_macd(data, short_window=12, long_window=26, signal_window=9):
    short_ema = data['Adj Close'].ewm(span=short_window, adjust=False).mean()
    long_ema = data['Adj Close'].ewm(span=long_window, adjust=False).mean()
    macd = short_ema - long_ema
    signal = macd.ewm(span=signal_window, adjust=False).mean()
    return macd, signal

# Function to calculate SMA
def calculate_sma(data, window=50):
    return data['Adj Close'].rolling(window=window).mean()

# Function to forecast future values using Prophet (better for time series)
def forecast_with_prophet(data, column, periods=126):
    df = pd.DataFrame()
    df['ds'] = data.index
    df['y'] = data[column].values
    
    # Train Prophet model
    model = Prophet(yearly_seasonality=True, daily_seasonality=False)
    model.fit(df)
    
    # Create a future dataframe for forecasting
    future = model.make_future_dataframe(periods=periods, freq='B')
    forecast = model.predict(future)
    
    forecast_dates = forecast['ds'][-periods:]
    forecast_values = forecast['yhat'][-periods:]
    
    forecast_df = pd.DataFrame({'Date': forecast_dates, column: forecast_values})
    forecast_df.set_index('Date', inplace=True)
    
    return forecast_df

# Streamlit App for S&P 500 Indicator Prediction
st.title("S&P 500 Indicator Prediction for Next 6 Months")

# Fetch S&P 500 data for the last 15 years
data = get_data_from_yfinance(ticker)

# Calculate technical indicators
data['RSI'] = calculate_rsi(data)
data['MACD'], data['Signal Line'] = calculate_macd(data)
data['SMA'] = calculate_sma(data)

# Remove missing values (from rolling calculations)
data.dropna(inplace=True)

# Forecast for 6 months ahead using Prophet, starting from next month
forecast_periods = 126  # Approx. 6 months of business days
rsi_forecast = forecast_with_prophet(data, 'RSI', forecast_periods)
macd_forecast = forecast_with_prophet(data, 'MACD', forecast_periods)
price_forecast = forecast_with_prophet(data, 'Adj Close', forecast_periods)

# Limit the data to show only the last year
data = data[data.index >= pd.Timestamp(datetime.date.today() - datetime.timedelta(days=365))]

# Plot RSI, MACD on separate graphs, and SMA on the same graph as S&P 500 price
st.subheader("S&P 500 Price with SMA and Technical Indicators (RSI, MACD)")

# Initialize the plot for Price and SMA
fig_price = go.Figure()

# Plot S&P 500 Price
fig_price.add_trace(go.Scatter(x=data.index, y=data['Adj Close'], mode='lines', name='S&P 500 Price', line=dict(color='blue')))

# Add checkbox for SMA
show_sma = st.checkbox('Show SMA on Price Chart', value=True)

# Plot SMA
if show_sma:
    fig_price.add_trace(go.Scatter(x=data.index, y=data['SMA'], mode='lines', name='SMA', line=dict(color='red')))
    fig_price.add_trace(go.Scatter(x=price_forecast.index, y=price_forecast['Adj Close'], mode='lines', name='SMA Forecast', line=dict(color='orange', dash='dash')))

# Customize layout for price and SMA
fig_price.update_layout(title="S&P 500 Price and SMA with 6-Month Forecast", xaxis_title="Date", yaxis_title="Price (USD)", template="plotly_white")
st.plotly_chart(fig_price)

# Plot RSI separately
st.subheader("RSI with 6-Month Forecast")
fig_rsi = go.Figure()
fig_rsi.add_trace(go.Scatter(x=data.index, y=data['RSI'], mode='lines', name='RSI', line=dict(color='green')))
fig_rsi.add_trace(go.Scatter(x=rsi_forecast.index, y=rsi_forecast['RSI'], mode='lines', name='RSI Forecast', line=dict(color='orange', dash='dash')))
fig_rsi.update_layout(title="RSI with 6-Month Forecast", xaxis_title="Date", yaxis_title="RSI", template="plotly_white")
st.plotly_chart(fig_rsi)

# Plot MACD separately
st.subheader("MACD with 6-Month Forecast")
fig_macd = go.Figure()
fig_macd.add_trace(go.Scatter(x=data.index, y=data['MACD'], mode='lines', name='MACD', line=dict(color='purple')))
fig_macd.add_trace(go.Scatter(x=macd_forecast.index, y=macd_forecast['MACD'], mode='lines', name='MACD Forecast', line=dict(color='orange', dash='dash')))
fig_macd.update_layout(title="MACD with 6-Month Forecast", xaxis_title="Date", yaxis_title="MACD", template="plotly_white")
st.plotly_chart(fig_macd)


# =============================== Section 2: Interactive Trade Tracker ===============================

# Streamlit App for Trade Tracker
st.title("Interactive Trade Tracker with Dividends, Trade Markers, and Profit/Loss Calculations")

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

# Limit the date range based on user input
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

# Customize layout for stock prices
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
