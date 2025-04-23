import os
import pandas as pd
import requests
import datetime

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
    從 Alpha Vantage API 獲取每日匯率數據。

    Returns:
        dict: 包含每日匯率數據的字典。
    """
    print("Fetching exchange rate data...")
    params = {
        'function': 'FX_DAILY',  # API 功能參數，指定要獲取的數據類型
        'from_symbol': FROM_SYMBOL,  # 基礎貨幣
        'to_symbol': TO_SYMBOL,  # 目標貨幣
        'apikey': API_KEY  # API 金鑰
    }
    response = requests.get(BASE_URL, params=params)
    data = response.json()
    print("Exchange rate data fetched.")
    return data.get(TIME_SERIES_KEY, {})

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
    ma60 = df['MA60'].iloc[-1]  # 獲取最新的 MA60 值

    if latest_rate < ma60:
        log_rate_below_ma60(latest_date, latest_rate, ma60)
    else:
        print(f"No logging needed: Rate {latest_rate} is above MA60 {ma60} on {latest_date}")

def main():
    """
    主程序流程：獲取匯率數據，計算 MA60，並檢查和記錄匯率狀況。
    """
    print("Starting main process...")
    data = fetch_exchange_rate()  # 獲取匯率數據
    df = calculate_ma60(data)  # 計算 MA60
    check_and_log(df)  # 檢查並記錄匯率狀況
    print("Main process completed.")

if __name__ == '__main__':
    main()
