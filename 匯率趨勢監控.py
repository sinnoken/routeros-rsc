import os
import pandas as pd
import requests
from datetime import datetime, timedelta

# 使用環境變數來獲取 API 金鑰
API_KEY = os.getenv('ALPHA_VANTAGE_API')
BASE_URL = 'https://www.alphavantage.co/query'

# 定義貨幣符號和資料鍵名
FROM_SYMBOL = 'USD'
TO_SYMBOL = 'TWD'
TIME_SERIES_KEY = 'Time Series FX (Daily)'
CLOSE_PRICE_KEY = '4. close'
LOG_FILE = 'exchange_rate_log.txt'

def fetch_exchange_rate():
    print("Fetching exchange rate data...")
    params = {
        'function': 'FX_DAILY',
        'from_symbol': FROM_SYMBOL,
        'to_symbol': TO_SYMBOL,
        'apikey': API_KEY,
        'outputsize': 'full'  # 確保獲取完整的數據集
    }
    response = requests.get(BASE_URL, params=params)
    data = response.json()

    # 獲取當前日期和一年前的日期
    today = datetime.now()
    one_year_ago = today - timedelta(days=700)

    # 提取一年的數據
    time_series = data.get(TIME_SERIES_KEY, {})
    filtered_data = {date: values for date, values in time_series.items() if one_year_ago <= datetime.strptime(date, '%Y-%m-%d') <= today}

    print("Exchange rate data fetched.")
    return filtered_data

def calculate_moving_averages(data):
    print("Calculating moving averages...")
    df = pd.DataFrame(data).T  # 轉置數據以便日期作為索引
    df.index = pd.to_datetime(df.index)  # 將索引轉換為日期時間格式
    df = df.sort_index()  # 按日期排序
    df[CLOSE_PRICE_KEY] = df[CLOSE_PRICE_KEY].astype(float)  # 將收盤價轉換為浮點數類型以便計算
    # 計算21日移動平均
    df['MA21'] = df[CLOSE_PRICE_KEY].rolling(window=21).mean()
    # 計算60日移動平均
    df['MA60'] = df[CLOSE_PRICE_KEY].rolling(window=60).mean()
    # 計算75日移動平均
    df['MA75'] = df[CLOSE_PRICE_KEY].rolling(window=75).mean()
    # 計算297日移動平均
    df['MA297'] = df[CLOSE_PRICE_KEY].rolling(window=297).mean()
    print("Moving averages calculation completed.")
    return df
    
def check_and_log(df):
    print("Checking latest rate against MA...")
    latest_date = df.index[-1]  # 獲取最新日期
    
    latest_rate = df[CLOSE_PRICE_KEY].iloc[-1]  # 獲取最新匯率
    ma21  = df['MA21'].iloc[-1]
    ma60  = df['MA60'].iloc[-1]
    ma75  = df['MA75'].iloc[-1]
    ma297 = df['MA297'].iloc[-1]

    # 計算價格差
    price_difference = ma75 - latest_rate
    percentage_difference = (price_difference / ma75) * 100

    existing_value = os.getenv('RATE_BELOW_MA60', '')
    
    # 檢查 latest_rate 是否小於 MA60
    if latest_rate < ma75:
        message = (
            f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: 最新匯率: {latest_rate:.2f} 小於 MA75: {ma75:.2f}，價格差: {price_difference:.2f}，百分比差異: {percentage_difference:.2f}%。"
        )
        print(message)
        with open(os.environ['GITHUB_ENV'], 'a') as env_file:
            env_file.write(f"RATE_BELOW_MA60={existing_value.strip() + message.strip()}\n")
            existing_value = os.getenv('RATE_BELOW_MA60', '')
        print("環境變數 RATE_BELOW_MA60 已設定。")
    else:
        print(
            f"無需記錄：最新匯率 {latest_rate:.2f} 高於 MA75 {ma75:.2f}，日期: {latest_date}"
        )

    # 檢查 MA21 < MA297 < MA75
    if ma21 < ma297 < ma75:
        message = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: MA21:{ma21:.2f} 小於 MA297:{ma297:.2f} 小於 MA75:{ma75:.2f}，價格差: {price_difference:.2f}。"
        print(message)
        with open(os.environ['GITHUB_ENV'], 'a') as env_file:
            env_file.write(f"RATE_BELOW_MA60={existing_value.strip() + message.strip()}\n")
            existing_value = os.getenv('RATE_BELOW_MA60', '')
        print("Environment variable RATE_BELOW_MA60 set.")
    else:
        print(f"No logging needed: MA21 {ma21:.2f} 不小於 MA297 {ma297:.2f} or MA297 不小於 MA75 {ma75:.2f} on {latest_date}")

    # 檢查 MA75 < MA297 < MA21
    if ma75 < ma297 < ma21:
        message = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: MA75:{ma75:.2f} 小於 MA297:{ma297:.2f} 小於 MA21:{ma21:.2f}，價格差: {price_difference:.2f}。"
        print(message)
        with open(os.environ['GITHUB_ENV'], 'a') as env_file:
            env_file.write(f"RATE_BELOW_MA60={existing_value.strip() + message.strip()}\n")
            existing_value = os.getenv('RATE_BELOW_MA60', '')
        print("Environment variable RATE_BELOW_MA60 set.")
    else:
        print(f"No logging needed: MA75 {ma75:.2f} 不小於 MA297 {ma297:.2f} or MA297 不小於 MA21 {ma21:.2f} on {latest_date}")

def main():
    print("Starting main process...")
    data = fetch_exchange_rate()  # 獲取匯率數據
    df = calculate_moving_averages(data)  # 計算 
    check_and_log(df)  # 檢查並記錄匯率狀況
    print("Main process completed.")

if __name__ == '__main__':
    main()
