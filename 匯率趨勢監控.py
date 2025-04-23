import os
import pandas as pd
from alpha_vantage.foreignexchange import ForeignExchange
from alpha_vantage.techindicators import TechIndicators
import datetime

# 使用環境變數來獲取 API 金鑰
API_KEY = os.getenv('ALPHA_VANTAGE_API')

# 定義貨幣符號和資料鍵名
FROM_SYMBOL = 'USD'
TO_SYMBOL = 'TWD'
LOG_FILE = 'exchange_rate_log.txt'

def fetch_exchange_rate():
    """
    從 Alpha Vantage API 獲取每日匯率數據。

    Returns:
        pd.DataFrame: 包含每日匯率數據的資料框。
    """
    print("Fetching exchange rate data...")
    fx = ForeignExchange(key=API_KEY, output_format='pandas')
    data, _ = fx.get_currency_exchange_daily(from_symbol=FROM_SYMBOL, to_symbol=TO_SYMBOL, outputsize='full')
    print("Exchange rate data fetched.")
    return data

def calculate_ma60(data):
    """
    計算匯率數據的60日移動平均線（MA60）。

    Args:
        data (pd.DataFrame): 包含每日匯率數據的資料框。

    Returns:
        pd.DataFrame: 包含匯率和 MA60 的資料框。
    """
    print("Calculating MA60...")
    ti = TechIndicators(key=API_KEY, output_format='pandas')
    ma60, _ = ti.get_sma(symbol=f'{FROM_SYMBOL}/{TO_SYMBOL}', interval='daily', time_period=60, series_type='close')
    data['MA60'] = ma60['SMA']
    print("MA60 calculation completed.")
    return data

def log_rate_below_ma60(latest_date, latest_rate, ma60):
    """
    當最新匯率低於 MA60 時，將事件記錄到日誌文件中。

    Args:
        latest_date (datetime): 最新匯率的日期。
        latest_rate (float): 最新匯率。
        ma60 (float): 最新的 MA60 值。
    """
    with open(LOG_FILE, 'a') as log_file:
        log_file.write(f"{datetime.datetime.now()}: Rate {latest_rate} fell below MA60 {ma60} on {latest_date}\n")
    print(f"Logged: Rate {latest_rate} fell below MA60 {ma60} on {latest_date}")

def check_and_log(df):
    """
    檢查最新匯率是否低於 MA60，若是則記錄到日誌中。

    Args:
        df (pd.DataFrame): 包含匯率和 MA60 的資料框。
    """
    print("Checking latest rate against MA60...")
    latest_date = df.index[-1]  # 獲取最新日期
    latest_rate = df['4. close'].iloc[-1]  # 獲取最新匯率
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
