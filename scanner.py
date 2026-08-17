import os
import requests
import json
from datetime import datetime, timezone

ALPACA_API_KEY = os.environ["ALPACA_API_KEY"]
ALPACA_SECRET_KEY = os.environ["ALPACA_SECRET_KEY"]

TICKERS = [
    "AAPL", "MSFT", "NVDA", "AMZN", "META", "GOOGL", "TSLA",
    "MU", "AMD", "AVGO", "ARM", "TSM", "ASML", "LRCX", "AMAT",
    "KLAC", "MRVL", "QCOM", "INTC", "NXPI", "ON", "MPWR", "MCHP",
    "ADI", "TXN", "WDC", "STX", "SNDK", "ALAB", "CRDO", "SMCI",
    "DELL", "HPE", "CLS", "JBL", "APH", "TEL", "ACLS", "AEHR",
    "COHU", "CAMT", "LSCC", "QRVO", "SWKS", "NBIS", "CRWV", "VRT",
    "ANET", "AAOI", "LITE", "COHR", "CIEN", "FN", "GLW", "KEYS",
    "NTAP", "PSTG", "GEV", "ETN", "CEG", "VST", "NRG", "PWR",
    "HUBB", "EME", "FIX", "MOD", "BE", "OKLO", "SMR", "NNE", "CCJ",
    "LEU", "UEC", "UUUU", "BWXT", "TLN", "PLTR", "ORCL", "CRM",
    "NOW", "APP", "CRWD", "PANW", "NET", "DDOG", "SNOW", "MDB",
    "GTLB", "PATH", "IOT", "S", "FTNT", "CYBR", "ZS", "OKTA", "TEAM",
    "HUBS", "ESTC", "CFLT", "DOCN", "TWLO", "RDDT", "SHOP", "UBER",
    "DASH", "ABNB", "RBLX", "DUOL", "CVNA", "AFRM", "SOFI", "HOOD",
    "COIN", "MSTR", "CAVA", "CELH", "ELF", "ONON", "BROS", "TOST",
    "HIMS", "SE", "MELI", "PDD", "BABA", "JD", "GRAB", "RIVN", "LCID",
    "IONQ", "RGTI", "QBTS", "QUBT", "RKLB", "ASTS", "LUNR", "RDW",
    "BKSY", "PL", "AVAV", "KTOS", "RCAT", "JOBY", "ACHR", "LDOS",
    "HII", "LLY", "ISRG", "TGTX", "TWST", "VKTX", "CRSP", "RXRX",
    "TEM", "OSCR", "PRAX", "LGND", "MRNA", "BNTX", "VRTX", "REGN",
    "ALNY", "GH", "NTRA", "RARE", "BEAM", "JPM", "GS", "V", "MA",
    "XYZ", "PYPL", "NU", "UPST", "LMND", "ROOT", "IBKR", "SCHW", "C",
    "BAC", "KKR", "APO", "BX", "AA", "FCX", "CLF", "MP", "ALB",
    "SQM", "CDE", "AG", "HL", "NEM", "GOLD", "X", "NUE", "STLD",
    "TECK", "VALE", "RIO", "XOM", "CVX", "COP", "OXY", "FANG", "DVN",
    "EOG", "SLB", "HAL", "BKR", "LNG", "EQT", "RRC", "AR", "CTRA",
    "FSLR", "ENPH", "RUN", "NXT", "FLNC", "STEM", "QS", "CHPT",
    "BLDP", "CAT", "DE", "URI", "PH", "HON", "RTX", "GE", "NFLX",
    "ADBE", "INTU", "COST", "WMT", "AMGN", "BKNG", "MAR", "CMG", "SPOT"
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


def get_signal(symbol, bars):
    if len(bars) < 1001:
        return {
            "symbol": symbol,
            "signal": "INSUFFICIENT_HISTORY"
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
            "signal": "INSUFFICIENT_HISTORY"
        }

    pct_rank_b = rank * -1

    if pct_rank_b <= -95:
        signal = "STRONG_BUY"
    elif pct_rank_b <= -85:
        signal = "BUY"
    else:
        signal = "NONE"

    latest = bars[-1]

    return {
        "symbol": symbol,
        "signal": signal,
        "date": latest["t"][:10],
        "close": str(latest["c"])
    }


results = []

try:
    print("Downloading Alpaca market data...")
    all_bars = download_all_bars()
    print("Download complete.")

    for ticker in TICKERS:
        try:
            result = get_signal(ticker, all_bars.get(ticker, []))
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

print(f"Finished. Scanned {len(results)} tickers.")
