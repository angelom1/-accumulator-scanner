import os
import requests
import json

ALPACA_API_KEY = os.environ["ALPACA_API_KEY"]
ALPACA_SECRET_KEY = os.environ["ALPACA_SECRET_KEY"]

TICKERS = [
    # MEGA CAP / AI / SEMICONDUCTORS
    "AAPL", "MSFT", "NVDA", "AMZN", "META", "GOOGL", "TSLA",
    "AMD", "AVGO", "MU", "QCOM", "INTC", "AMAT", "LRCX", "KLAC",
    "MRVL", "NXPI", "ON", "ADI", "TXN", "WDC", "STX", "ANET",
    "VRT", "SMCI", "DELL",

    # SOFTWARE / CLOUD / CYBERSECURITY
    "PLTR", "ORCL", "CRM", "NOW", "APP", "CRWD", "PANW", "NET",
    "DDOG", "SNOW", "MDB", "TEAM", "OKTA", "ZS", "FTNT",

    # INTERNET / FINTECH / HIGH-BETA CONSUMER TECH
    "UBER", "ABNB", "DASH", "SHOP", "PYPL", "SOFI", "HOOD", "COIN",
    "MSTR", "RBLX", "DUOL", "AFRM", "CVNA", "SE", "MELI", "SPOT",

    # POWER / INDUSTRIAL / ENERGY
    "VST", "CEG", "NRG", "ETN", "PWR", "BE", "CCJ", "UEC",
    "FSLR", "ENPH", "XOM", "CVX", "COP", "OXY", "SLB", "GE",
    "CAT", "URI",

    # FINANCIALS
    "JPM", "GS", "BAC", "C", "SCHW", "IBKR", "V", "MA", "KKR",
    "APO", "BX",

    # HEALTHCARE / BIOTECH MOMENTUM
    "LLY", "ISRG", "VRTX", "REGN", "ALNY", "NTRA", "MRNA", "UNH",

    # CONSUMER MOMENTUM
    "CELH", "ELF", "ONON", "BROS", "HIMS", "CMG"
]


def laguerre(series, g):
    l0, l1, l2, l3, out = [], [], [], [], []

    for i, p in enumerate(series):
        prev_l0 = l0[i - 1] if i > 0 else 0.0
        prev_l1 = l1[i - 1] if i > 0 else 0.0
        prev_l2 = l2[i - 1] if i > 0 else 0.0
        prev_l3 = l3[i - 1] if i > 0 else 0.0

        cur_l0 = (1 - g) * p + g * prev_l0
        cur_l1 = -g * cur_l0 + prev_l0 + g * prev_l1
        cur_l2 = -g * cur_l1 + prev_l1 + g * prev_l2
        cur_l3 = -g * cur_l2 + prev_l2 + g * prev_l3

        l0.append(cur_l0)
        l1.append(cur_l1)
        l2.append(cur_l2)
        l3.append(cur_l3)

        out.append(
            (cur_l0 + 2 * cur_l1 + 2 * cur_l2 + cur_l3) / 6
        )

    return out


def percent_rank_current(values, length=1000):
    if len(values) < length + 1:
        return None

    current = values[-1]
    previous_values = values[-(length + 1):-1]
    less_or_equal = sum(1 for v in previous_values if v <= current)

    return (less_or_equal / length) * 100


def download_all_bars():
    url = "https://data.alpaca.markets/v2/stocks/bars"

    headers = {
        "APCA-API-KEY-ID": ALPACA_API_KEY,
        "APCA-API-SECRET-KEY": ALPACA_SECRET_KEY,
    }

    params = {
        "symbols": ",".join(TICKERS),
        "timeframe": "1Day",
        "start": "2021-01-01T00:00:00Z",
        "limit": 10000,
        "adjustment": "raw",
        "feed": "iex",
        "sort": "asc",
    }

    all_bars = {ticker: [] for ticker in TICKERS}
    page_token = None

    while True:
        if page_token:
            params["page_token"] = page_token
        elif "page_token" in params:
            del params["page_token"]

        response = requests.get(
            url,
            headers=headers,
            params=params,
            timeout=60
        )

        response.raise_for_status()
        data = response.json()

        for symbol, bars in data.get("bars", {}).items():
            if symbol in all_bars:
                all_bars[symbol].extend(bars)

        page_token = data.get("next_page_token")

        if not page_token:
            break

    return all_bars


def get_reference_date(all_bars):
    latest_dates = []

    for bars in all_bars.values():
        if bars:
            latest_dates.append(bars[-1]["t"][:10])

    if not latest_dates:
        raise RuntimeError("No market data was returned by Alpaca.")

    return max(latest_dates)


def get_signal(symbol, bars, reference_date):
    if not bars:
        return {
            "symbol": symbol,
            "signal": "NO_DATA"
        }

    latest = bars[-1]
    latest_date = latest["t"][:10]

    # Prevent stale historical data from producing a current signal.
    if latest_date < reference_date:
        return {
            "symbol": symbol,
            "signal": "STALE_DATA",
            "date": latest_date,
            "reference_date": reference_date,
            "close": str(latest["c"])
        }

    if len(bars) < 1001:
        return {
            "symbol": symbol,
            "signal": "INSUFFICIENT_HISTORY",
            "date": latest_date
        }

    hl2 = [
        (float(row["h"]) + float(row["l"])) / 2
        for row in bars
    ]

    lmas = laguerre(hl2, 0.4)
    lmal = laguerre(hl2, 0.8)

    ppo_b = []

    for fast, slow in zip(lmas, lmal):
        if slow == 0:
            ppo_b.append(0.0)
        else:
            ppo_b.append(((slow - fast) / slow) * 100)

    rank = percent_rank_current(ppo_b, 1000)

    if rank is None:
        return {
            "symbol": symbol,
            "signal": "INSUFFICIENT_HISTORY",
            "date": latest_date
        }

    pct_rank_b = rank * -1

    if pct_rank_b <= -95:
        signal = "STRONG_BUY"
    elif pct_rank_b <= -85:
        signal = "BUY"
    else:
        signal = "NONE"

    return {
        "symbol": symbol,
        "signal": signal,
        "date": latest_date,
        "close": str(latest["c"])
    }


results = []

try:
    print("Downloading Alpaca market data...")

    all_bars = download_all_bars()

    print("Download complete.")

    reference_date = get_reference_date(all_bars)

    print(f"Freshest market date: {reference_date}")

    for ticker in TICKERS:
        try:
            result = get_signal(
                ticker,
                all_bars.get(ticker, []),
                reference_date
            )

            results.append(result)
            print(result)

        except Exception as e:
            result = {
                "symbol": ticker,
                "signal": "ERROR",
                "message": str(e)
            }

            results.append(result)
            print(result)

except Exception as e:
    raise RuntimeError(f"Alpaca data download failed: {e}")


with open("signals.json", "w") as f:
    json.dump(results, f, indent=2)


summary = {}

for result in results:
    signal = result["signal"]
    summary[signal] = summary.get(signal, 0) + 1


print("")
print("SCAN SUMMARY")
print("------------")

for signal, count in sorted(summary.items()):
    print(f"{signal}: {count}")

print("")
print(f"Finished. Scanned {len(results)} tickers.")
