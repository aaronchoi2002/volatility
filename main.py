import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
pd.set_option("display.float_format", "{:.2f}".format)
st.title("Volatility Dashboard")

# User input for stock code and period

stock_code = st.sidebar.text_input("Enter the stock code:", value="AAPL") 
period = st.sidebar.number_input("Enter the period for the rolling:", value=50, step=1)
x_days = st.sidebar.number_input("Enter the number of days volatility:", value=1, step=1)
v_alert = (st.sidebar.number_input("Average volatility Higher/Low than pervious (%):", value=0, step=1)/100)
    
if st.sidebar.button('Refresh'):
    st.experimental_rerun()



# Set the end date as today and the start date as 180 days before today
end_date = datetime.today()
start_date = end_date - timedelta(days=1800)
# Download historical data as dataframe
def download_data(stock_code, start_date, end_date):
    data = yf.download(stock_code, start=start_date, end=end_date)
    return data

def download_data_current(stock_code):
    data_c = yf.download(stock_code, period="1d", interval="1m")
    return data_c   




data = download_data(stock_code, start_date, end_date)
if data.empty:
    raise ValueError(f"No data available for the stock code: {stock_code}")


# Calculate the daily high and low prices
data["daily_volatility"] = data["High"] - data["Low"]
data["std_daily_volatility"] = data["daily_volatility"].rolling(period).std()
data["avg_daily_volatility"] = data["daily_volatility"].rolling(period).mean()


# Calculate the x-day high and low prices
data["x_day_high"] = data["High"].rolling(window=x_days).max()
data["x_day_low"] = data["Low"].rolling(window=x_days).min()
data["x_day_volatility"] = data["x_day_high"] - data["x_day_low"]
data["std_x_day_volatility"] = data["x_day_volatility"].rolling(period).std()
data["avg_x_day_volatility"] = data["x_day_volatility"].rolling(period).mean()


# Calculate the weekly high and low prices
start_date_wk = end_date - timedelta(days=900)
data_wk = yf.download(stock_code, start=start_date_wk, end=end_date, interval="1wk")
data_wk["weekly_volatility"] = data_wk["High"] - data_wk["Low"]
data_wk["std_weekly_volatility"] = data_wk["weekly_volatility"].rolling(period).std()
data_wk["avg_weekly_volatility"] = data_wk["weekly_volatility"].rolling(period).mean()


data_c = download_data_current(stock_code)
current_price = data_c["Close"].iloc[-1]
update_time = data_c.index[-1]  
st.markdown(f"""
<span style="font-size: 34px; color: green;">
Price: {round(current_price,2)}
</span>
""", unsafe_allow_html=True)
st.write("Last update time: ", update_time)
# Create tabs
tab1, tab2, tab3 = st.tabs(["Today Volatility", f"{x_days}-Day Volatility", "Weekly Volatility"])
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
        Today Range: {round(day_high - day_low,2)}
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
        upper_std_v_1 = day_average_volatility + (day_std_volatility * 1)
        lower_std_v_1 = day_average_volatility - (day_std_volatility * 1)
        if lower_std_v_1 < 0:
            lower_std_v_1 = 0.0   
        st.metric(label="1 Std Deviation", value=f"{lower_std_v_1:.5} - {upper_std_v_1:.5}")
        st.markdown(f'<span style="color: blue;">Previous day volatility: {day_volatility}</span>', unsafe_allow_html=True)

    with col2:
        # 2 Std Deviation
        upper_std_v_2 = day_average_volatility + (day_std_volatility * 2)
        lower_std_v_2 = day_average_volatility - (day_std_volatility * 2)
        if lower_std_v_2 < 0:
            lower_std_v_2 = 0.0
        st.metric(label="2 Std Deviation", value=f"{lower_std_v_2:.5} - {upper_std_v_2:.5}")
        st.markdown(f'<span style="color: blue;">Average {period} volatility: {day_average_volatility}</span>',
                    unsafe_allow_html=True)

    with col3:
        # 3 Std Deviation
        upper_std_v_3 = day_average_volatility + (day_std_volatility * 3)
        lower_std_v_3 = day_average_volatility - (day_std_volatility * 3)
        if lower_std_v_3 < 0:
            lower_std_v_3 = 0.0
        st.metric(label="3 Std Deviation", value=f"{lower_std_v_3:.5} - {upper_std_v_3:.5}")
        st.markdown(f'<span style="color: blue;">Std Deviation of volatility: {day_std_volatility}</span>',
                    unsafe_allow_html=True)
    st.write("Previous day: ", data.index[-2])

    st.write("_________________________")
    if day_volatility > day_average_volatility *(1+v_alert):
        st.markdown(f"""
        <span style="font-size: 34px; color: red;">
        Sell
        </span>
        """, unsafe_allow_html=True)
        st.markdown(f"""
        <span style="font-size: 24px; color: red;">
        Previous day volatility: {day_volatility} is higher than average volatility: {day_average_volatility}
        </span>
        """, unsafe_allow_html=True)
    elif day_volatility < day_average_volatility *(1-v_alert):
        st.markdown(f"""
        <span style="font-size: 34px; color: green;">
        Buy
        </span>
        """, unsafe_allow_html=True)
        st.markdown(f"""
        <span style="font-size: 24px; color: green;">
        Previous day volatility: {day_volatility} is lower than average volatility: {day_average_volatility}
        </span>
        """, unsafe_allow_html=True)

    csv =data.to_csv().encode('utf-8')
    st.download_button(
        label="Download data as CSV",
        data=csv,
        file_name='daily_volatility.csv',
        mime='text/csv',
        )   
    
with tab2:

    # Display the last 2-day volatility

    day_x_volatility = round(data["x_day_volatility"].iloc[-2], 2)
    day_x_average_volatility = round(data["avg_x_day_volatility"].iloc[-1], 2)
    day_x_std_volatility = round(data["std_x_day_volatility"].iloc[-1], 2)
    day_x_high = round(data["x_day_high"].iloc[-1], 2)
    day_x_low = round(data["x_day_low"].iloc[-1], 2)
    col1, col2 = st.columns(2)
    with col1:
        #show daily high and low different
        st.markdown(f"""
        <span style="font-size: 24px; color: green;">
        {x_days}-Day Range: {round(day_x_high - day_x_low,2)}
        </span>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <span style="font-size: 24px; color: green;">
        {x_days}-Day high: {day_x_high}<br>
        {x_days}-Day low: {day_x_low}
        </span>
        """, unsafe_allow_html=True)

    st.write("_________________________")


    col1, col2, col3 = st.columns(3)
    with col1:
        # 1 Std Deviation
        upper_x_std_v_1 = day_x_average_volatility + (day_x_std_volatility * 1)
        lower_x_std_v_1 = day_x_average_volatility - (day_x_std_volatility * 1)
        if lower_x_std_v_1 < 0:
            lower_x_std_v_1 = 0.0
        st.metric(label="1 Std Deviation", value=f"{lower_x_std_v_1:.5} - {upper_x_std_v_1:.5}")
        st.markdown(f'<span style="color: blue;">Previous volatility: {day_x_volatility}</span>', unsafe_allow_html=True)

    with col2:
        # 2 Std Deviation
        upper_x_std_v_2 = day_x_average_volatility + (day_x_std_volatility * 2)
        lower_x_std_v_2 = day_x_average_volatility - (day_x_std_volatility * 2)
        if lower_x_std_v_2 < 0:
            lower_x_std_v_2 = 0.0
        st.metric(label="2 Std Deviation", value=f"{lower_x_std_v_2:.5} - {upper_x_std_v_2:.5}")
        st.markdown(f'<span style="color: blue;">Average {period} volatility: {day_x_average_volatility}</span>',
                    unsafe_allow_html=True)

    with col3:
        # 3 Std Deviation
        upper_x_std_v_3 = day_x_average_volatility + (day_x_std_volatility * 3)
        lower_x_std_v_3 = day_x_average_volatility - (day_x_std_volatility * 3)
        if lower_x_std_v_3 < 0:
            lower_x_std_v_3 = 0.0
        st.metric(label="3 Std Deviation", value=f"{lower_x_std_v_3:.5} - {upper_x_std_v_3:.5}")
        st.markdown(f'<span style="color: blue;">Std Deviation of volatility: {day_x_std_volatility}</span>',
                    unsafe_allow_html=True)
    st.write(f"Previous {x_days}-day: ", data.index[-2])

    st.write("_________________________")
    if day_x_volatility > day_x_average_volatility *(1+v_alert):
        st.markdown(f"""
        <span style="font-size: 34px; color: red;">
        Sell
        </span>
        """, unsafe_allow_html=True)
        st.markdown(f"""
        <span style="font-size: 24px; color: red;">
        Previous {x_days}-day volatility: {day_x_volatility} is higher than average volatility: {day_x_average_volatility}
        </span>
        """, unsafe_allow_html=True)
    elif day_x_volatility < day_x_average_volatility *(1-v_alert):
        st.markdown(f"""
        <span style="font-size: 34px; color: green;">
        Buy
        </span>
        """, unsafe_allow_html=True)
        st.markdown(f"""
        <span style="font-size: 24px; color: green;">
        Previous {x_days}-day volatility: {day_x_volatility} is lower than average volatility: {day_x_average_volatility}
        </span>
        """, unsafe_allow_html=True)
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
        Weeky Range: {round(week_high - week_low,2)}
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
        upper_w_std_v_1 = week_average_volatility + (week_std_volatility * 1)
        lower_w_std_v_1 = week_average_volatility - (week_std_volatility * 1)
        if lower_w_std_v_1 < 0:
            lower_w_std_v_1 = 0.0
        st.metric(label="1 Std Deviation", value=f"{lower_w_std_v_1:.5} - {upper_w_std_v_1:.5}")
        st.markdown(f'<span style="color: blue;">Previous week volatility: {week_volatility}</span>', unsafe_allow_html=True)

    with col2:
        # 2 Std Deviation
        upper_w_std_v_2 = week_average_volatility + (week_std_volatility * 2)
        lower_w_std_v_2 = week_average_volatility - (week_std_volatility * 2)
        if lower_w_std_v_2 < 0:
            lower_w_std_v_2 = 0.0
        st.metric(label="2 Std Deviation", value=f"{lower_w_std_v_2:.5} - {upper_w_std_v_2:.5}")
        st.markdown(f'<span style="color: blue;">Average {period} volatility: {week_average_volatility}</span>',
                    unsafe_allow_html=True)

    with col3:
        # 3 Std Deviation
        upper_w_std_v_3 = week_average_volatility + (week_std_volatility * 3)
        lower_w_std_v_3 = week_average_volatility - (week_std_volatility * 3)
        if lower_w_std_v_3 < 0:
            lower_w_std_v_3 = 0.0
        st.metric(label="3 Std Deviation", value=f"{lower_w_std_v_3:.5} - {upper_w_std_v_3:.5}")
        st.markdown(f'<span style="color: blue;">Std Deviation of volatility: {week_std_volatility}</span>',
                    unsafe_allow_html=True)
    st.write("Previous week: ", data_wk.index[-2])
    st.write("_________________________")
    if week_volatility > week_average_volatility *(1+v_alert):
        st.markdown(f"""
        <span style="font-size: 34px; color: red;">
        Sell
        </span>
        """, unsafe_allow_html=True)
        st.markdown(f"""
        <span style="font-size: 24px; color: red;">
        Previous week volatility: {week_volatility} is higher than average volatility: {week_average_volatility}
        </span>
        """, unsafe_allow_html=True)
    elif week_volatility < week_average_volatility *(1-v_alert):
        st.markdown(f"""
        <span style="font-size: 34px; color: green;">
        Buy
        </span>
        """, unsafe_allow_html=True)
        st.markdown(f"""
        <span style="font-size: 24px; color: green;">
        Previous week volatility: {week_volatility} is lower than average volatility: {week_average_volatility}
        </span>
        """, unsafe_allow_html=True)

    csv =data_wk.to_csv().encode('utf-8')
    st.download_button(
        label="Download data as CSV",
        data=csv,
        file_name='Weekly_volatility.csv',
        mime='text/csv',
        )   
st.write("_________________________")
