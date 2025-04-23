import os
import pandas as pd
import requests
import datetime

# 使用環境變數來獲取 API 金鑰
API_KEY = os.getenv('ALPHA_VANTAGE_API')
BASE_URL = 'https://www.alphavantage.co/query'

def fetch_exchange_rate():
    params = {
        'function': 'FX_DAILY',
        'from_symbol': 'TWD',
        'to_symbol': 'USD',
        'apikey': API_KEY
    }
    response = requests.get(BASE_URL, params=params)
    data = response.json()
    return data['Time Series FX (Daily)']

def calculate_ma60(data):
    df = pd.DataFrame(data).T
    df.index = pd.to_datetime(df.index)
    df = df.sort_index()
    df['4. close'] = df['4. close'].astype(float)
    df['MA60'] = df['4. close'].rolling(window=60).mean()
    return df

def check_and_log(df):
    latest_date = df.index[-1]
    latest_rate = df['4. close'].iloc[-1]
    ma60 = df['MA60'].iloc[-1]

    if latest_rate < ma60:
        with open('exchange_rate_log.txt', 'a') as log_file:
            log_file.write(f"{datetime.datetime.now()}: Rate {latest_rate} fell below MA60 {ma60} on {latest_date}\n")
        print(f"Logged: Rate {latest_rate} fell below MA60 {ma60} on {latest_date}")

def main():
    data = fetch_exchange_rate()
    df = calculate_ma60(data)
    check_and_log(df)

if __name__ == '__main__':
    main()
