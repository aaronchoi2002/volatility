import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

st.title("Volatility Dashboard")

# User input for stock code and period
stock_code = st.sidebar.text_input("Enter the stock code:", value="AAPL")
period = st.sidebar.number_input("Enter the period for the rolling:", value=50, step=1)
x_days = st.sidebar.number_input("Enter the number of days volatility:", value=1, step=1)

pd.set_option("display.float_format", "{:.2f}".format)

# Set the end date as today and the start date as 180 days before today
end_date = datetime.today()
start_date = end_date - timedelta(days=180)

# Download historical data as dataframe
data = yf.download(stock_code, start=start_date, end=end_date)


# Calculate the daily high and low prices
data["daily_volatility"] = data["High"] - data["Low"]
data["std_daily_volatility"] = data["daily_volatility"].rolling(period).std()
data["avg_daily_volatility"] = data["daily_volatility"].rolling(period).mean()


# Calculate the 2-day high and low prices
data["2_day_high"] = data["High"].rolling(window=x_days).max()
data["2_day_low"] = data["Low"].rolling(window=x_days).min()
data["2_day_volatility"] = data["2_day_high"] - data["2_day_low"]
data["std_2_day_volatility"] = data["2_day_volatility"].rolling(period).std()
data["avg_2_day_volatility"] = data["2_day_volatility"].rolling(period).mean()


# Calculate the weekly high and low prices
start_date_wk = end_date - timedelta(days=900)
data_wk = yf.download(stock_code, start=start_date_wk, end=end_date, interval="1wk")
data_wk["weekly_volatility"] = data_wk["High"] - data_wk["Low"]
data_wk["std_weekly_volatility"] = data_wk["weekly_volatility"].rolling(period).std()
data_wk["avg_weekly_volatility"] = data_wk["weekly_volatility"].rolling(period).mean()






# Create tabs
tab1, tab2, tab3 = st.tabs(["Daily Volatility", f"{x_days}-Day Volatility", "Weekly Volatility"])
with tab1:
    # Display the last daily volatility
    
    day_volatility = round(data["daily_volatility"].iloc[-2], 2)
    day_average_volatility = round(data["avg_daily_volatility"].iloc[-2], 2)
    day_std_volatility = round(data["std_daily_volatility"].iloc[-2], 2)
    day_high = round(data["High"].iloc[-1], 2)
    day_low = round(data["Low"].iloc[-1], 2)
    col1, col2 = st.columns(2)
    with col1:
        #show daily high and low different
        st.markdown(f"""
        <span style="font-size: 24px; color: green;">
        Daily Diff: {round(day_high - day_low,2)}
        </span>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <span style="font-size: 24px; color: green;">
        Day high: {day_high}<br>
        Day low: {day_low}
        </span>
        """, unsafe_allow_html=True)

    st.write("_________________________")
    col1, col2, col3 = st.columns(3)
    with col1:
        # 1 Std Deviation
        std_v_1 = day_average_volatility + (day_std_volatility * 1)
        st.metric(label="1 Std Deviation", value=f"{std_v_1:.5}")
        st.markdown(f'<span style="color: blue;">Last volatility: {day_volatility}</span>', unsafe_allow_html=True)

    with col2:
        # 2 Std Deviation
        std_v_2 = day_average_volatility + (day_std_volatility * 2)
        st.metric(label="2 Std Deviation", value=f"{std_v_2:.5}")
        st.markdown(f'<span style="color: blue;">Average {period} volatility: {day_average_volatility}</span>',
                    unsafe_allow_html=True)

    with col3:
        # 3 Std Deviation
        std_v_3 = day_average_volatility + (day_std_volatility * 3)
        st.metric(label="3 Std Deviation", value=f"{std_v_3:.5}")
        st.markdown(f'<span style="color: blue;">Std Deviation of volatility: {day_std_volatility}</span>',
                    unsafe_allow_html=True)
    st.write("Last volatility date: ", data.index[-2])

with tab2:

    # Display the last 2-day volatility

    day_2_volatility = round(data["2_day_volatility"].iloc[-1], 2)
    day_2_average_volatility = round(data["avg_2_day_volatility"].iloc[-1], 2)
    day_2_std_volatility = round(data["std_2_day_volatility"].iloc[-1], 2)
    day_2_high = round(data["2_day_high"].iloc[-1], 2)
    day_2_low = round(data["2_day_low"].iloc[-1], 2)
    col1, col2 = st.columns(2)
    with col1:
        #show daily high and low different
        st.markdown(f"""
        <span style="font-size: 24px; color: green;">
        {x_days}-Day Diff: {round(day_2_high - day_2_low,2)}
        </span>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <span style="font-size: 24px; color: green;">
        {x_days}-Day high: {day_2_high}<br>
        {x_days}-Day low: {day_2_low}
        </span>
        """, unsafe_allow_html=True)

    st.write("_________________________")


    col1, col2, col3 = st.columns(3)
    with col1:
        # 1 Std Deviation
        std_v_1 = day_2_average_volatility + (day_2_std_volatility * 1)
        st.metric(label="1 Std Deviation", value=f"{std_v_1:.5}")
        st.markdown(f'<span style="color: blue;">Last volatility: {day_2_volatility}</span>', unsafe_allow_html=True)

    with col2:
        # 2 Std Deviation
        std_v_2 = day_2_average_volatility + (day_2_std_volatility * 2)
        st.metric(label="2 Std Deviation", value=f"{std_v_2:.5}")
        st.markdown(f'<span style="color: blue;">Average {period} volatility: {day_2_average_volatility}</span>',
                    unsafe_allow_html=True)

    with col3:
        # 3 Std Deviation
        std_v_3 = day_2_average_volatility + (day_2_std_volatility * 3)
        st.metric(label="3 Std Deviation", value=f"{std_v_3:.5}")
        st.markdown(f'<span style="color: blue;">Std Deviation of volatility: {day_2_std_volatility}</span>',
                    unsafe_allow_html=True)

with tab3:

    # Display the last weekly volatility

    week_volatility = round(data_wk["weekly_volatility"].iloc[-2], 2)
    week_average_volatility = round(data_wk["avg_weekly_volatility"].iloc[-2], 2)
    week_std_volatility = round(data_wk["std_weekly_volatility"].iloc[-2], 2)
    week_high = round(data_wk["High"].iloc[-1], 2)
    week_low = round(data_wk["Low"].iloc[-1], 2)
    col1, col2 = st.columns(2)
    with col1:
        #show daily high and low different
        st.markdown(f"""
        <span style="font-size: 24px; color: green;">
        Weeky Diff: {round(week_high - week_low,2)}
        </span>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <span style="font-size: 24px; color: green;">
        Day high: {week_high}<br>
        Day low: {week_low}
        </span>
        """, unsafe_allow_html=True)

    st.write("_________________________")
    col1, col2, col3 = st.columns(3)
    with col1:
        # 1 Std Deviation
        std_v_1 = week_average_volatility + (week_std_volatility * 1)
        st.metric(label="1 Std Deviation", value=f"{std_v_1:.5}")
        st.markdown(f'<span style="color: blue;">Last volatility: {week_volatility}</span>', unsafe_allow_html=True)

    with col2:
        # 2 Std Deviation
        std_v_2 = week_average_volatility + (week_std_volatility * 2)
        st.metric(label="2 Std Deviation", value=f"{std_v_2:.5}")
        st.markdown(f'<span style="color: blue;">Average {period} volatility: {week_average_volatility}</span>',
                    unsafe_allow_html=True)

    with col3:
        # 3 Std Deviation
        std_v_3 = week_average_volatility + (week_std_volatility * 3)
        st.metric(label="3 Std Deviation", value=f"{std_v_3:.5}")
        st.markdown(f'<span style="color: blue;">Std Deviation of volatility: {week_std_volatility}</span>',
                    unsafe_allow_html=True)

st.write("_________________________")
