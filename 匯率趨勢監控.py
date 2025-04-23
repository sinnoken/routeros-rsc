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
    """
    從 Alpha Vantage API 獲取一年的每日匯率數據。

    Returns:
        dict: 包含一年的每日匯率數據的字典。
    """
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

def calculate_ma60(data):
    """
    計算匯率數據的60日移動平均線（MA60）。

    Args:
        data (dict): 包含每日匯率數據的字典。

    Returns:
        pd.DataFrame: 包含匯率和 MA60 的資料框。
    """
    print("Calculating MA60...")
    df = pd.DataFrame(data).T  # 轉置數據以便日期作為索引
    df.index = pd.to_datetime(df.index)  # 將索引轉換為日期時間格式
    df = df.sort_index()  # 按日期排序
    df[CLOSE_PRICE_KEY] = df[CLOSE_PRICE_KEY].astype(float)  # 將收盤價轉換為浮點數
    df['MA60'] = df[CLOSE_PRICE_KEY].rolling(window=60).mean()  # 計算60日移動平均
    print("MA60 calculation completed.")
    return df
    
def calculate_moving_averages(data):
    """
    計算匯率數據的21日、60日、75日和297日移動平均線（MA21、MA60、MA75、MA297）。

    Args:
        data (dict): 包含每日匯率數據的字典，其中鍵為日期（字串格式），值為包含匯率信息的字典。

    Returns:
        pd.DataFrame: 包含每日匯率和對應的 MA21、MA60、MA75、MA297 的資料框。
                      資料框的索引為日期，列包括匯率的收盤價和計算出的移動平均線。
    """
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
    
def log_rate_below_ma60(latest_date, latest_rate, ma60):
    """
    當最新匯率低於 MA60 時，將事件記錄到日誌文件中。

    Args:
        latest_date (datetime): 最新匯率的日期。
        latest_rate (float): 最新匯率。
        ma60 (float): 最新的 MA60 值。
    """
    log_message = f"{datetime.datetime.now()}: Rate {latest_rate} fell below MA60 {ma60} on {latest_date}\n"

    # 記錄到日誌文件
    with open(LOG_FILE, 'a') as log_file:
        log_file.write(log_message)
    print(f"Logged: {log_message.strip()}")

    # 設置環境變數
    os.environ['RATE_BELOW_MA60'] = log_message.strip()

    # 將環境變數寫入 $GITHUB_ENV
    with open(os.environ['GITHUB_ENV'], 'a') as env_file:
        env_file.write(f"RATE_BELOW_MA60={log_message.strip()}\n")
    
    print("Environment variable RATE_BELOW_MA60 set.")

def check_and_log(df):
    """
    檢查最新匯率是否低於 MA60，若是則記錄到日誌中。

    Args:
        df (pd.DataFrame): 包含匯率和 MA60 的資料框。
    """
    print("Checking latest rate against MA60...")
    latest_date = df.index[-1]  # 獲取最新日期
    latest_rate = df[CLOSE_PRICE_KEY].iloc[-1]  # 獲取最新匯率
    
    ma21  = df['MA21'].iloc[-1]  # 獲取最新的 MA21 值
    ma60  = df['MA60'].iloc[-1]  # 獲取最新的 MA60 值
    ma75  = df['MA75'].iloc[-1]  # 獲取最新的 MA60 值
    ma297 = df['MA297'].iloc[-1]  # 獲取最新的 MA297 值

    # 檢查 MA21 是否小於 MA297 且 MA297 是否小於 MA75
    if ma21 < ma297:
        print(f"{datetime.datetime.now()}: ma21:{ma21} < ma297:{ma297} < ma75:{ma75} on {latest_date}\n")
        log_message = f"{datetime.datetime.now()}: ma21:{ma21} < ma297:{ma297} < ma75:{ma75} on {latest_date}\n"
        with open(os.environ['GITHUB_ENV'], 'a') as env_file:
            env_file.write(f"RATE_BELOW_MA60={log_message.strip()}\n")
        print("Environment variable RATE_BELOW_MA60 set.")
        log_rate_below_ma60(latest_date, ma21, ma297)
    else:
        print(f"No logging needed: MA21 {ma21} is above MA297 {ma297} on {latest_date}")
    
    # 檢查 MA75 是否小於 MA297 且 MA297 是否小於 MA21
    if ma75 < ma297 < ma21:
        print(f"{datetime.datetime.now()}: ma75:{ma75} < ma297:{ma297} < ma21:{ma21} on {latest_date}\n")
        log_message = f"{datetime.datetime.now()}: ma75:{ma75} < ma297:{ma297} < ma21:{ma21} on {latest_date}\n"
        with open(os.environ['GITHUB_ENV'], 'a') as env_file:
            env_file.write(f"RATE_BELOW_MA60={log_message.strip()}\n")
        print("Environment variable RATE_BELOW_MA60 set.")
        log_rate_below_ma60(latest_date, ma21, ma297)
    else:
        print(f"No logging needed: MA75 {ma75} is above MA297 {ma297} on {latest_date}")

def main():
    """
    主程序流程：獲取匯率數據，計算 MA60，並檢查和記錄匯率狀況。
    """
    print("Starting main process...")
    data = fetch_exchange_rate()  # 獲取匯率數據
    df = calculate_moving_averages(data)  # 計算 
    check_and_log(df)  # 檢查並記錄匯率狀況
    print("Main process completed.")

if __name__ == '__main__':
    main()
