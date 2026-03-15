# 生成的最终版本的代码
# 可以运行，但可以发现还是有 bug

# 通过 streamlit run <your_script_name.py> 命令启动

import streamlit as st
import requests
import logging
import pandas as pd
from datetime import datetime, timedelta

# 设置日志
logging.basicConfig(level=logging.INFO, filename='app.log', format='%(asctime)s - %(levelname)s - %(message)s')


# 获取比特币当前价格和24小时变化数据的函数
def fetch_bitcoin_data():
    try:
        response = requests.get(
            'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd&include_24hr_change=true')
        response.raise_for_status()
        data = response.json()

        if "bitcoin" in data and "usd" in data["bitcoin"] and "usd_24h_change" in data["bitcoin"]:
            price = data['bitcoin']['usd']
            price_change = data['bitcoin']['usd_24h_change']
            price_change_amount = (price_change / 100) * price
            return price, price_change, price_change_amount
        else:
            logging.error("数据格式有误")
            st.error("获取的数据格式有误，请稍后重试。")
            return None, None, None
    except requests.exceptions.RequestException as e:
        logging.error(f"请求异常: {e}")
        st.error("无法获取数据，请检查网络连接或重试。")
        return None, None, None


# 获取指定小时的比特币价格历史数据
def fetch_price_history(hours):
    try:
        end_time = int(datetime.now().timestamp())
        start_time = int((datetime.now() - timedelta(hours=hours)).timestamp())
        url = f'https://api.coingecko.com/api/v3/coins/bitcoin/market_chart/range?vs_currency=usd&from={start_time}&to={end_time}'
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        prices = data['prices']
        price_series = [(datetime.fromtimestamp(p[0] / 1000), p[1]) for p in prices]
        return pd.DataFrame(price_series, columns=["Time", "Price"]).set_index("Time")
    except requests.exceptions.RequestException as e:
        logging.error(f"价格历史请求异常: {e}")
        st.error("无法获取价格历史数据，请稍后重试。")
        return None


# 显示数据的辅助函数
def display_data(price, change_percent, change_amount):
    st.subheader(f"当前比特币价格: ${price:,.2f} USD")
    if change_percent is not None:
        st.write(f"24小时变化: {change_amount:,.2f} USD ({change_percent:.2f}%)")
        st.success("价格上涨" if change_percent >= 0 else "价格下跌")


def main():
    st.title("比特币价格显示应用")

    # 用户选择时间范围
    time_range = st.selectbox("选择显示的时间范围:", options=[1, 24, 168],
                              format_func=lambda x: f"过去{x} {'小时' if x < 24 else '天'}")

    # 用户设置自动刷新频率
    refresh_interval = st.selectbox("选择自动刷新频率:", options=[1, 5, 10], format_func=lambda x: f"每{x}分钟刷新")

    # 初始化数据和价格历史
    price, change_percent, change_amount = fetch_bitcoin_data()

    if price is not None:
        display_data(price, change_percent, change_amount)

        with st.spinner("正在加载价格历史数据..."):
            price_history = fetch_price_history(time_range)
            if price_history is not None:
                st.line_chart(price_history['Price'])
    else:
        if st.button("重试获取数据"):
            main()  # 尝试重新加载数据

    # 手动刷新按钮
    if st.button("刷新价格"):
        price, change_percent, change_amount = fetch_bitcoin_data()
        if price is not None:
            st.success("价格已更新！")
            display_data(price, change_percent, change_amount)

    # 设置自动刷新间隔
    if st.session_state.get('auto_refresh', False):
        st.experimental_rerun()  # 在刷新期间自动重载

    # 开始定时器
    st.session_state.auto_refresh = True


if __name__ == "__main__":
    main()

