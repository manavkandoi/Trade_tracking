import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objs as go
from prophet import Prophet
import datetime

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
    model = Prophet(yearly_seasonality=True, daily_seasonality=True)
    model.fit(df)
    
    # Create a future dataframe for forecasting
    future = model.make_future_dataframe(periods=periods, freq='B')
    forecast = model.predict(future)
    
    forecast_dates = forecast['ds'][-periods:]
    forecast_values = forecast['yhat'][-periods:]
    
    forecast_df = pd.DataFrame({'Date': forecast_dates, column: forecast_values})
    forecast_df.set_index('Date', inplace=True)
    
    return forecast_df

# Streamlit App
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

# **Fix: Limit the data to show only the last year**
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
