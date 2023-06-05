import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

st.set_page_config(
    page_title="多页面波幅仪表板",
    page_icon="📈",
)

pd.set_option("display.float_format", "{:.2f}".format)
st.title("波幅仪表板")

# 用户输入股票代码和周期
stock_code = st.sidebar.text_input("输入股票代码：", value="AAPL")
period = st.sidebar.number_input("输入滚动周期：", value=50, step=1)
x_days = st.sidebar.number_input("输入几天的波幅：", value=1, step=1)
v_alert = (st.sidebar.number_input("平均波幅高于/低于前一日的百分比：", value=0, step=1) / 100)

if st.sidebar.button('刷新'):
    st.experimental_rerun()

# 将结束日期设为今天，开始日期设为今天之前180天
end_date = datetime.today()
start_date = end_date - timedelta(days=1800)
# 下载历史数据并转为数据框
def download_data(stock_code, start_date, end_date):
    data = yf.download(stock_code, start=start_date, end=end_date)
    return data

def download_data_current(stock_code):
    data_c = yf.download(stock_code, period="1d", interval="1m")
    return data_c

data = download_data(stock_code, start_date, end_date)
if data.empty:
    raise ValueError(f"股票代码 {stock_code} 无数据可用")

# 计算每日最高和最低价格
data["daily_volatility"] = data["High"] - data["Low"]
data["std_daily_volatility"] = data["daily_volatility"].rolling(period).std()
data["avg_daily_volatility"] = data["daily_volatility"].rolling(period).mean()

# 计算x天的最高和最低价格
data["x_day_high"] = data["High"].rolling(window=x_days).max()
data["x_day_low"] = data["Low"].rolling(window=x_days).min()
data["x_day_volatility"] = data["x_day_high"] - data["x_day_low"]
data["std_x_day_volatility"] = data["x_day_volatility"].rolling(period).std()
data["avg_x_day_volatility"] = data["x_day_volatility"].rolling(period).mean()

# 计算每周最高和最低价格
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
价格：{round(current_price,2)}
</span>
""", unsafe_allow_html=True)
st.write("上次更新时间：", update_time)

# 创建选项卡
tab1, tab2, tab3 = st.tabs(["今日波幅", f"{x_days}天波幅", "周波幅"])
with tab1:
    # 显示最后一个交易日的波幅
    day_volatility = round(data["daily_volatility"].iloc[-2], 2)
    day_average_volatility = round(data["avg_daily_volatility"].iloc[-2], 2)
    day_std_volatility = round(data["std_daily_volatility"].iloc[-2], 2)
    day_high = round(data["High"].iloc[-1], 2)
    day_low = round(data["Low"].iloc[-1], 2)
    col1, col2 = st.columns(2)
    with col1:
        # 显示当天的高点和低点差异
        st.markdown(f"""
        <span style="font-size: 24px; color: green;">
        今日区间：{round(day_high - day_low,2)}
        </span>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <span style="font-size: 24px; color: green;">
        最高价：{day_high}<br>
        最低价：{day_low}
        </span>
        """, unsafe_allow_html=True)

    st.write("_________________________")
    col1, col2, col3 = st.columns(3)
    with col1:
        # 1个标准差
        upper_std_v_1 = day_average_volatility + (day_std_volatility * 1)
        lower_std_v_1 = day_average_volatility - (day_std_volatility * 1)
        if lower_std_v_1 < 0:
            lower_std_v_1 = 0.0   
        st.metric(label="1个标准差", value=f"{lower_std_v_1:.5} - {upper_std_v_1:.5}")
        st.markdown(f'<span style="color: blue;">前一天波幅：{day_volatility}</span>', unsafe_allow_html=True)

    with col2:
        # 2个标准差
        upper_std_v_2 = day_average_volatility + (day_std_volatility * 2)
        lower_std_v_2 = day_average_volatility - (day_std_volatility * 2)
        if lower_std_v_2 < 0:
            lower_std_v_2 = 0.0
        st.metric(label="2个标准差", value=f"{lower_std_v_2:.5} - {upper_std_v_2:.5}")
        st.markdown(f'<span style="color: blue;">平均{period}波幅：{day_average_volatility}</span>', unsafe_allow_html=True)

    with col3:
        # 3个标准差
        upper_std_v_3 = day_average_volatility + (day_std_volatility * 3)
        lower_std_v_3 = day_average_volatility - (day_std_volatility * 3)
        if lower_std_v_3 < 0:
            lower_std_v_3 = 0.0
        st.metric(label="3个标准差", value=f"{lower_std_v_3:.5} - {upper_std_v_3:.5}")
        st.markdown(f'<span style="color: blue;">波幅的标准差：{day_std_volatility}</span>', unsafe_allow_html=True)
    st.write("前一天：", data.index[-2])

    st.write("_________________________")
    if day_volatility > day_average_volatility * (1 + v_alert):
        st.markdown(f"""
        <span style="font-size: 34px; color: red;">
        卖出
        </span>
        """, unsafe_allow_html=True)
        st.markdown(f"""
        <span style="font-size: 24px; color: red;">
        前一天波幅：{day_volatility} 高于平均波幅：{day_average_volatility}
        </span>
        """, unsafe_allow_html=True)
    elif day_volatility < day_average_volatility * (1 - v_alert):
        st.markdown(f"""
        <span style="font-size: 34px; color: green;">
        买进
        </span>
        """, unsafe_allow_html=True)
        st.markdown(f"""
        <span style="font-size: 24px; color: green;">
        前一天波幅：{day_volatility} 低于平均波幅：{day_average_volatility}
        </span>
        """, unsafe_allow_html=True)

    csv = data.to_csv().encode('utf-8')
    st.download_button(
        label="下载数据为CSV",
        data=csv,
        file_name='daily_volatility.csv',
        mime='text/csv',
    )   

with tab2:
    # 显示最后x天的波幅
    day_x_volatility = round(data["x_day_volatility"].iloc[-2], 2)
    day_x_average_volatility = round(data["avg_x_day_volatility"].iloc[-1], 2)
    day_x_std_volatility = round(data["std_x_day_volatility"].iloc[-1], 2)
    day_x_high = round(data["x_day_high"].iloc[-1], 2)
    day_x_low = round(data["x_day_low"].iloc[-1], 2)
    col1, col2 = st.columns(2)
    with col1:
        # 显示每天的高点和低点差异
        st.markdown(f"""
        <span style="font-size: 24px; color: green;">
        {x_days}天区间：{round(day_x_high - day_x_low,2)}
        </span>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <span style="font-size: 24px; color: green;">
        {x_days}天高点：{day_x_high}<br>
        {x_days}天低点：{day_x_low}
        </span>
        """, unsafe_allow_html=True)

    st.write("_________________________")

    col1, col2, col3 = st.columns(3)
    with col1:
        # 1个标准差
        upper_x_std_v_1 = day_x_average_volatility + (day_x_std_volatility * 1)
        lower_x_std_v_1 = day_x_average_volatility - (day_x_std_volatility * 1)
        if lower_x_std_v_1 < 0:
            lower_x_std_v_1 = 0.0
        st.metric(label="1个标准差", value=f"{lower_x_std_v_1:.5} - {upper_x_std_v_1:.5}")
        st.markdown(f'<span style="color: blue;">前{x_days}天波幅：{day_x_volatility}</span>', unsafe_allow_html=True)

    with col2:
        # 2个标准差
        upper_x_std_v_2 = day_x_average_volatility + (day_x_std_volatility * 2)
        lower_x_std_v_2 = day_x_average_volatility - (day_x_std_volatility * 2)
        if lower_x_std_v_2 < 0:
            lower_x_std_v_2 = 0.0
        st.metric(label="2个标准差", value=f"{lower_x_std_v_2:.5} - {upper_x_std_v_2:.5}")
        st.markdown(f'<span style="color: blue;">平均{period}波幅：{day_x_average_volatility}</span>', unsafe_allow_html=True)

    with col3:
        # 3个标准差
        upper_x_std_v_3 = day_x_average_volatility + (day_x_std_volatility * 3)
        lower_x_std_v_3 = day_x_average_volatility - (day_x_std_volatility * 3)
        if lower_x_std_v_3 < 0:
            lower_x_std_v_3 = 0.0
        st.metric(label="3个标准差", value=f"{lower_x_std_v_3:.5} - {upper_x_std_v_3:.5}")
        st.markdown(f'<span style="color: blue;">波幅的标准差：{day_x_std_volatility}</span>', unsafe_allow_html=True)
    st.write(f"前{x_days}天：", data.index[-2])

    st.write("_________________________")
    if day_x_volatility > day_x_average_volatility * (1 + v_alert):
        st.markdown(f"""
        <span style="font-size: 34px; color: red;">
        卖出
        </span>
        """, unsafe_allow_html=True)
        st.markdown(f"""
        <span style="font-size: 24px; color: red;">
        前{x_days}天波幅：{day_x_volatility} 高于平均波幅：{day_x_average_volatility}
        </span>
        """, unsafe_allow_html=True)
    elif day_x_volatility < day_x_average_volatility * (1 - v_alert):
        st.markdown(f"""
        <span style="font-size: 34px; color: green;">
        买进
        </span>
        """, unsafe_allow_html=True)
        st.markdown(f"""
        <span style="font-size: 24px; color: green;">
        前{x_days}天波幅：{day_x_volatility} 低于平均波幅：{day_x_average_volatility}
        </span>
        """, unsafe_allow_html=True)
with tab3:
    # 显示最后一周的波幅
    week_volatility = round(data_wk["weekly_volatility"].iloc[-2], 2)
    week_average_volatility = round(data_wk["avg_weekly_volatility"].iloc[-2], 2)
    week_std_volatility = round(data_wk["std_weekly_volatility"].iloc[-2], 2)
    week_high = round(data_wk["High"].iloc[-1], 2)
    week_low = round(data_wk["Low"].iloc[-1], 2)
    col1, col2 = st.columns(2)
    with col1:
        # 显示每周的高点和低点差异
        st.markdown(f"""
        <span style="font-size: 24px; color: green;">
        周区间：{round(week_high - week_low,2)}
        </span>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <span style="font-size: 24px; color: green;">
        本周高价：{week_high}<br>
        本周低价：{week_low}
        </span>
        """, unsafe_allow_html=True)

    st.write("_________________________")
    col1, col2, col3 = st.columns(3)
    with col1:
        # 1个标准差
        upper_w_std_v_1 = week_average_volatility + (week_std_volatility * 1)
        lower_w_std_v_1 = week_average_volatility - (week_std_volatility * 1)
        if lower_w_std_v_1 < 0:
            lower_w_std_v_1 = 0.0
        st.metric(label="1个标准差", value=f"{lower_w_std_v_1:.5} - {upper_w_std_v_1:.5}")
        st.markdown(f'<span style="color: blue;">前一周波幅：{week_volatility}</span>', unsafe_allow_html=True)

    with col2:
        # 2个标准差
        upper_w_std_v_2 = week_average_volatility + (week_std_volatility * 2)
        lower_w_std_v_2 = week_average_volatility - (week_std_volatility * 2)
        if lower_w_std_v_2 < 0:
            lower_w_std_v_2 = 0.0
        st.metric(label="2个标准差", value=f"{lower_w_std_v_2:.5} - {upper_w_std_v_2:.5}")
        st.markdown(f'<span style="color: blue;">平均{period}波幅：{week_average_volatility}</span>', unsafe_allow_html=True)

    with col3:
        # 3个标准差
        upper_w_std_v_3 = week_average_volatility + (week_std_volatility * 3)
        lower_w_std_v_3 = week_average_volatility - (week_std_volatility * 3)
        if lower_w_std_v_3 < 0:
            lower_w_std_v_3 = 0.0
        st.metric(label="3个标准差", value=f"{lower_w_std_v_3:.5} - {upper_w_std_v_3:.5}")
        st.markdown(f'<span style="color: blue;">波幅的标准差：{week_std_volatility}</span>', unsafe_allow_html=True)
    st.write("前一周：", data_wk.index[-2])
    st.write("_________________________")
    if week_volatility > week_average_volatility * (1 + v_alert):
        st.markdown(f"""
        <span style="font-size: 34px; color: red;">
        卖出
        </span>
        """, unsafe_allow_html=True)
        st.markdown(f"""
        <span style="font-size: 24px; color: red;">
        前一周波幅：{week_volatility} 高于平均波幅：{week_average_volatility}
        </span>
        """, unsafe_allow_html=True)
    elif week_volatility < week_average_volatility * (1 - v_alert):
        st.markdown(f"""
        <span style="font-size: 34px; color: green;">
        买进
        </span>
        """, unsafe_allow_html=True)
        st.markdown(f"""
        <span style="font-size: 24px; color: green;">
        前一周波幅：{week_volatility} 低于平均波幅：{week_average_volatility}
        </span>
        """, unsafe_allow_html=True)

    csv = data_wk.to_csv().encode('utf-8')
    st.download_button(
        label="下载数据为CSV",
        data=csv,
        file_name='Weekly_volatility.csv',
        mime='text/csv',
    )   
st.write("_________________________")
