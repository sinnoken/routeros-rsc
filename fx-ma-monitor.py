import os
from datetime import datetime
from typing import Any

import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


# API 設定
BASE_URL = "https://www.alphavantage.co/query"
API_KEY_ENV = "ALPHA_VANTAGE_API"

# 貨幣設定
FROM_SYMBOL = "USD"
TO_SYMBOL = "TWD"

# Alpha Vantage 回應欄位
DAILY_SERIES_KEY = "Time Series FX (Daily)"
REALTIME_RATE_KEY = "Realtime Currency Exchange Rate"
DAILY_CLOSE_KEY = "4. close"
CURRENT_RATE_KEY = "5. Exchange Rate"

# 均線設定
MA_WINDOWS = (21, 60, 75, 297)
HISTORY_OUTPUT_SIZE = "full"

# GitHub Actions 輸出
GITHUB_ALERT_VARIABLE = "RATE_ALERT"


def create_session() -> requests.Session:
    """建立具有重試機制的 HTTP Session。"""

    retry = Retry(
        total=3,
        connect=3,
        read=3,
        backoff_factor=1,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset({"GET"}),
        respect_retry_after_header=True,
    )

    session = requests.Session()
    session.mount(
        "https://",
        HTTPAdapter(max_retries=retry),
    )

    return session


def request_alpha_vantage(
    session: requests.Session,
    params: dict[str, str],
) -> dict[str, Any\]:
    """呼叫 Alpha Vantage 並檢查 HTTP、JSON 與 API 錯誤。"""

    response = session.get(
        BASE_URL,
        params=params,
        timeout=(10, 30),
    )
    response.raise_for_status()

    try:
        data = response.json()
    except requests.JSONDecodeError as error:
        raise RuntimeError(
            "Alpha Vantage 回傳的內容不是有效 JSON"
        ) from error

    if not isinstance(data, dict):
        raise RuntimeError("Alpha Vantage 回傳格式錯誤")

    for error_key in ("Error Message", "Note", "Information"):
        if error_key in data:
            raise RuntimeError(
                f"Alpha Vantage API 錯誤：{data[error_key]}"
            )

    return data


def fetch_daily_rates(
    session: requests.Session,
    api_key: str,
) -> dict[str, dict[str, str]\]:
    """取得 USD/TWD 歷史日線，供均線計算使用。"""

    data = request_alpha_vantage(
        session,
        {
            "function": "FX_DAILY",
            "from_symbol": FROM_SYMBOL,
            "to_symbol": TO_SYMBOL,
            "outputsize": HISTORY_OUTPUT_SIZE,
            "apikey": api_key,
        },
    )

    daily_rates = data.get(DAILY_SERIES_KEY)

    if not isinstance(daily_rates, dict) or not daily_rates:
        raise RuntimeError(
            f"API 回應缺少日線資料：{DAILY_SERIES_KEY}"
        )

    return daily_rates


def fetch_current_rate(
    session: requests.Session,
    api_key: str,
) -> float:
    """取得執行當下的 USD/TWD 匯率。"""

    data = request_alpha_vantage(
        session,
        {
            "function": "CURRENCY_EXCHANGE_RATE",
            "from_currency": FROM_SYMBOL,
            "to_currency": TO_SYMBOL,
            "apikey": api_key,
        },
    )

    realtime_data = data.get(REALTIME_RATE_KEY)

    if not isinstance(realtime_data, dict):
        raise RuntimeError(
            f"API 回應缺少即時匯率資料：{REALTIME_RATE_KEY}"
        )

    rate_value = realtime_data.get(CURRENT_RATE_KEY)

    if rate_value is None:
        raise RuntimeError(
            f"即時匯率資料缺少欄位：{CURRENT_RATE_KEY}"
        )

    try:
        return float(rate_value)
    except (TypeError, ValueError) as error:
        raise RuntimeError(
            f"無效的即時匯率：{rate_value}"
        ) from error


def build_rate_dataframe(
    daily_rates: dict[str, dict[str, str]],
) -> pd.DataFrame:
    """建立日線 DataFrame 並計算所有移動平均。"""

    dataframe = pd.DataFrame.from_dict(
        daily_rates,
        orient="index",
    )

    if DAILY_CLOSE_KEY not in dataframe.columns:
        raise ValueError(
            f"日線資料缺少收盤價欄位：{DAILY_CLOSE_KEY}"
        )

    dataframe.index = pd.to_datetime(
        dataframe.index,
        errors="coerce",
    )

    dataframe = (
        dataframe
        .loc[dataframe.index.notna()]
        .sort_index()
    )

    dataframe["close"] = pd.to_numeric(
        dataframe[DAILY_CLOSE_KEY],
        errors="coerce",
    )

    dataframe = dataframe.dropna(subset=["close"])

    required_entries = max(MA_WINDOWS)

    if len(dataframe) < required_entries:
        raise ValueError(
            f"歷史資料不足，MA{required_entries} 至少需要 "
            f"{required_entries} 筆，目前只有 {len(dataframe)} 筆"
        )

    for window in MA_WINDOWS:
        dataframe[f"MA{window}"] = (
            dataframe["close"]
            .rolling(
                window=window,
                min_periods=window,
            )
            .mean()
        )

    return dataframe


def evaluate_rate(
    dataframe: pd.DataFrame,
    current_rate: float,
) -> list[str\]:
    """將目前匯率與歷史日線均線比較。"""

    latest_row = dataframe.iloc[-1]
    latest_date = dataframe.index[-1]

    averages = {
        window: float(latest_row[f"MA{window}"])
        for window in MA_WINDOWS
    }

    values = pd.Series(
        {
            "current_rate": current_rate,
            **{
                f"MA{window}": value
                for window, value in averages.items()
            },
        }
    )

    if values.isna().any():
        invalid_values = values[values.isna()]
        raise ValueError(
            f"最新匯率或均線包含空值：\n{invalid_values}"
        )

    ma21 = averages[21]
    ma60 = averages[60]
    ma75 = averages[75]
    ma297 = averages[297]

    print_rate_status(
        current_rate=current_rate,
        latest_date=latest_date,
        averages=averages,
    )

    messages: list[str] = []

    append_below_ma_message(
        messages=messages,
        current_rate=current_rate,
        moving_average=ma60,
        label="MA60",
    )

    append_below_ma_message(
        messages=messages,
        current_rate=current_rate,
        moving_average=ma75,
        label="MA75",
    )

    if ma21 < ma297 < ma75:
        messages.append(
            "均線排列成立："
            f"MA21 {ma21:.4f} < "
            f"MA297 {ma297:.4f} < "
            f"MA75 {ma75:.4f}"
        )

    if ma75 < ma297 < ma21:
        messages.append(
            "均線排列成立："
            f"MA75 {ma75:.4f} < "
            f"MA297 {ma297:.4f} < "
            f"MA21 {ma21:.4f}"
        )

    return messages


def append_below_ma_message(
    messages: list[str],
    current_rate: float,
    moving_average: float,
    label: str,
) -> None:
    """目前匯率低於指定均線時加入通知。"""

    if current_rate >= moving_average:
        return

    difference = moving_average - current_rate
    percentage = difference / moving_average * 100

    messages.append(
        f"目前匯率 {current_rate:.4f} 低於 "
        f"{label} {moving_average:.4f}，"
        f"差距 {difference:.4f}，"
        f"低於 {percentage:.2f}%"
    )


def print_rate_status(
    current_rate: float,
    latest_date: pd.Timestamp,
    averages: dict[int, float],
) -> None:
    """顯示本次使用的匯率及均線資訊。"""

    print(f"目前 {FROM_SYMBOL}/{TO_SYMBOL}：{current_rate:.4f}")
    print(f"均線資料日期：{latest_date:%Y-%m-%d}")

    for window in MA_WINDOWS:
        print(f"MA{window}：{averages[window\]:.4f}")


def write_github_alert(messages: list[str]) -> None:
    """將通知寫入 GitHub Actions 環境變數。"""

    if not messages:
        print("目前沒有符合通知條件")
        return

    generated_at = datetime.now().astimezone().strftime(
        "%Y-%m-%d %H:%M:%S %Z"
    )

    alert = "\n".join(
        [
            f"{generated_at} {FROM_SYMBOL}/{TO_SYMBOL} 匯率通知",
            *messages,
        ]
    )

    print()
    print(alert)

    github_env = os.getenv("GITHUB_ENV")

    if not github_env:
        print("\n非 GitHub Actions 環境，不寫入 GITHUB_ENV")
        return

    delimiter = "RATE_ALERT_EOF"

    with open(
        github_env,
        "a",
        encoding="utf-8",
        newline="\n",
    ) as env_file:
        env_file.write(
            f"{GITHUB_ALERT_VARIABLE}<<{delimiter}\n"
        )
        env_file.write(alert)
        env_file.write(f"\n{delimiter}\n")


def main() -> None:
    """執行匯率下載、均線計算及通知判斷。"""

    api_key = os.getenv(API_KEY_ENV)

    if not api_key:
        raise RuntimeError(
            f"缺少環境變數：{API_KEY_ENV}"
        )

    print(
        f"開始檢查 {FROM_SYMBOL}/{TO_SYMBOL} 匯率..."
    )

    with create_session() as session:
        daily_rates = fetch_daily_rates(
            session=session,
            api_key=api_key,
        )

        dataframe = build_rate_dataframe(daily_rates)

        current_rate = fetch_current_rate(
            session=session,
            api_key=api_key,
        )

    messages = evaluate_rate(
        dataframe=dataframe,
        current_rate=current_rate,
    )

    write_github_alert(messages)

    print("匯率檢查完成")


if __name__ == "__main__":
    main()
