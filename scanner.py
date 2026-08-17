import os
import requests
import json

ALPACA_API_KEY = os.environ["ALPACA_API_KEY"]
ALPACA_SECRET_KEY = os.environ["ALPACA_SECRET_KEY"]


# ================================================================
# SWING TRADING UNIVERSE
# 187 listed entries / 185 unique symbols
# SOUN + VRT appear in multiple categories and are de-duplicated.
# ================================================================

TICKERS = list(dict.fromkeys([

    # ============================================================
    # NEOCLOUD / AI INFRASTRUCTURE
    # ============================================================
    "NBIS",
    "CRWV",
    "IREN",
    "APLD",
    "RIOT",
    "MARA",
    "CLSK",
    "HUT",
    "CIFR",
    "WULF",
    "CORZ",
    "BTDR",
    "SOUN",
    "LUNR",
    "GLXY",

    # ============================================================
    # AI SEMIS / HARDWARE
    # ============================================================
    "NVDA",
    "AMD",
    "AVGO",
    "ARM",
    "MRVL",
    "ASTS",
    "ALAB",
    "SMCI",
    "MU",
    "LRCX",
    "AMAT",
    "KLAC",
    "ON",
    "TER",
    "ENTG",
    "NXPI",
    "ADI",
    "MCHP",
    "WOLF",
    "GFS",
    "STX",
    "WDC",
    "SWKS",
    "QRVO",

    # ============================================================
    # AI SOFTWARE / CLOUD PLATFORMS
    # ============================================================
    "PLTR",
    "SNOW",
    "DDOG",
    "NET",
    "CRWD",
    "PANW",
    "ZS",
    "MDB",
    "NOW",
    "TEAM",
    "S",
    "GTLB",
    "CFLT",
    "ESTC",
    "AI",
    "BBAI",
    "SOUN",

    # ============================================================
    # MEGA-CAP AI / CLOUD ANCHORS
    # ============================================================
    "MSFT",
    "GOOGL",
    "GOOG",
    "AMZN",
    "META",
    "ORCL",
    "IBM",
    "CRM",
    "ADBE",
    "TSLA",

    # ============================================================
    # POWER / DATA CENTER INFRASTRUCTURE
    # ============================================================
    "VST",
    "CEG",
    "NRG",
    "TLN",
    "GEV",
    "ETN",
    "EMR",
    "VRT",
    "NVT",
    "PWR",

    # ============================================================
    # QUANTUM / FRONTIER TECH
    # ============================================================
    "IONQ",
    "RGTI",
    "QBTS",
    "QUBT",

    # ============================================================
    # FINTECH / CRYPTO-ADJACENT
    # ============================================================
    "COIN",
    "MSTR",
    "SOFI",
    "HOOD",
    "AFRM",
    "UPST",
    "PYPL",
    "SQ",

    # ============================================================
    # HIGH-BETA EV / AUTONOMY / SPACE
    # ============================================================
    "RIVN",
    "LCID",
    "NIO",
    "XPEV",
    "LI",
    "ACHR",
    "JOBY",
    "RKLB",

    # ============================================================
    # LEGACY SEMIS / TECH
    # ============================================================
    "INTC",
    "QCOM",
    "TXN",
    "CSCO",
    "HPE",
    "DELL",
    "JBL",
    "VRT",

    # ============================================================
    # BIOTECH / HEALTHCARE MOVERS
    # ============================================================
    "MRNA",
    "SRPT",
    "EXAS",
    "ALGN",
    "DXCM",
    "VRTX",
    "REGN",
    "ILMN",
    "BIIB",
    "CVRX",
    "KPTI",
    "BIOA",
    "MPLT",
    "SKYQ",

    # ============================================================
    # FINANCIALS
    # ============================================================
    "JPM",
    "GS",
    "MS",
    "BAC",
    "WFC",
    "SCHW",
    "C",
    "AXP",
    "BLK",
    "COF",

    # ============================================================
    # CONSUMER / RETAIL MOMENTUM
    # ============================================================
    "COST",
    "WMT",
    "NKE",
    "LULU",
    "CMG",
    "SBUX",
    "ABNB",
    "UBER",
    "DASH",
    "DKNG",
    "CVNA",
    "ETSY",
    "YETI",

    # ============================================================
    # INDUSTRIALS / DEFENSE
    # ============================================================
    "CAT",
    "DE",
    "BA",
    "LMT",
    "RTX",
    "GE",
    "HON",
    "GD",
    "NOC",

    # ============================================================
    # ENERGY
    # ============================================================
    "XOM",
    "CVX",
    "OXY",
    "SLB",
    "DVN",
    "FANG",
    "MPC",
    "VLO",

    # ============================================================
    # MATERIALS / MINING
    # ============================================================
    "FCX",
    "NEM",
    "MP",
    "AA",
    "X",
    "CLF",

    # ============================================================
    # AIRLINES / TRAVEL
    # ============================================================
    "DAL",
    "UAL",
    "CCL",
    "RCL",
    "EXPE",

    # ============================================================
    # COMMUNICATIONS / MEDIA
    # ============================================================
    "WBD",
    "PARA",
    "SPOT",
    "ROKU",
    "LYV",

    # ============================================================
    # BROAD / MACRO / SECTOR INSTRUMENTS
    # ============================================================
    "SPY",
    "QQQ",
    "IWM",
    "SMH",
    "XLK",
    "XLE",
    "XLF",
    "TLT",
    "GLD",
    "UVXY",
    "TQQQ",
    "SQQQ",
    "SOXL",
]))


# ================================================================
# LAGUERRE FILTER
# ================================================================

def laguerre(series, g):

    l0 = []
    l1 = []
    l2 = []
    l3 = []
    out = []

    for i, p in enumerate(series):

        prev_l0 = l0[i - 1] if i > 0 else 0.0
        prev_l1 = l1[i - 1] if i > 0 else 0.0
        prev_l2 = l2[i - 1] if i > 0 else 0.0
        prev_l3 = l3[i - 1] if i > 0 else 0.0

        cur_l0 = (
            (1 - g) * p
            + g * prev_l0
        )

        cur_l1 = (
            -g * cur_l0
            + prev_l0
            + g * prev_l1
        )

        cur_l2 = (
            -g * cur_l1
            + prev_l1
            + g * prev_l2
        )

        cur_l3 = (
            -g * cur_l2
            + prev_l2
            + g * prev_l3
        )

        l0.append(cur_l0)
        l1.append(cur_l1)
        l2.append(cur_l2)
        l3.append(cur_l3)

        out.append(
            (
                cur_l0
                + 2 * cur_l1
                + 2 * cur_l2
                + cur_l3
            ) / 6
        )

    return out


# ================================================================
# PERCENT RANK
# ================================================================

def percent_rank_current(
    values,
    length=1000
):

    if len(values) < length + 1:
        return None

    current = values[-1]

    previous_values = (
        values[-(length + 1):-1]
    )

    less_or_equal = sum(
        1
        for v in previous_values
        if v <= current
    )

    return (
        less_or_equal / length
    ) * 100


# ================================================================
# DOWNLOAD ALPACA DAILY BARS
# ================================================================

def download_all_bars():

    url = (
        "https://data.alpaca.markets"
        "/v2/stocks/bars"
    )

    headers = {
        "APCA-API-KEY-ID":
            ALPACA_API_KEY,

        "APCA-API-SECRET-KEY":
            ALPACA_SECRET_KEY,
    }

    params = {
        "symbols":
            ",".join(TICKERS),

        "timeframe":
            "1Day",

        "start":
            "2021-01-01T00:00:00Z",

        "limit":
            10000,

        "adjustment":
            "raw",

        "feed":
            "iex",

        "sort":
            "asc",
    }

    all_bars = {
        ticker: []
        for ticker in TICKERS
    }

    page_token = None

    while True:

        if page_token:

            params["page_token"] = (
                page_token
            )

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

        for symbol, bars in (
            data.get(
                "bars",
                {}
            ).items()
        ):

            if symbol in all_bars:

                all_bars[
                    symbol
                ].extend(
                    bars
                )

        page_token = data.get(
            "next_page_token"
        )

        if not page_token:
            break

    return all_bars


# ================================================================
# FIND FRESHEST MARKET DATE
# ================================================================

def get_reference_date(
    all_bars
):

    latest_dates = []

    for bars in (
        all_bars.values()
    ):

        if bars:

            latest_dates.append(
                bars[-1]["t"][:10]
            )

    if not latest_dates:

        raise RuntimeError(
            "No market data was "
            "returned by Alpaca."
        )

    return max(
        latest_dates
    )


# ================================================================
# CALCULATE ACCUMULATOR SIGNAL
# ================================================================

def get_signal(
    symbol,
    bars,
    reference_date
):

    # ------------------------------------------------------------
    # NO DATA
    # ------------------------------------------------------------

    if not bars:

        return {
            "symbol": symbol,
            "signal": "NO_DATA"
        }

    latest = bars[-1]

    latest_date = (
        latest["t"][:10]
    )


    # ------------------------------------------------------------
    # STALE-DATA SAFETY GUARD
    #
    # A ticker whose newest bar is older than the freshest market
    # date cannot produce BUY or STRONG_BUY.
    # ------------------------------------------------------------

    if latest_date < reference_date:

        return {
            "symbol":
                symbol,

            "signal":
                "STALE_DATA",

            "date":
                latest_date,

            "reference_date":
                reference_date,

            "close":
                str(
                    latest["c"]
                )
        }


    # ------------------------------------------------------------
    # 1000-DAY ACCUMULATOR HISTORY REQUIREMENT
    # ------------------------------------------------------------

    if len(bars) < 1001:

        return {
            "symbol":
                symbol,

            "signal":
                "INSUFFICIENT_HISTORY",

            "date":
                latest_date
        }


    # ------------------------------------------------------------
    # HL2
    # ------------------------------------------------------------

    hl2 = [
        (
            float(row["h"])
            + float(row["l"])
        ) / 2
        for row in bars
    ]


    # ------------------------------------------------------------
    # LAGUERRE MOVING AVERAGES
    # ------------------------------------------------------------

    lmas = laguerre(
        hl2,
        0.4
    )

    lmal = laguerre(
        hl2,
        0.8
    )


    # ------------------------------------------------------------
    # PPO
    # ------------------------------------------------------------

    ppo_b = []

    for fast, slow in zip(
        lmas,
        lmal
    ):

        if slow == 0:

            ppo_b.append(
                0.0
            )

        else:

            ppo_b.append(
                (
                    (
                        slow
                        - fast
                    )
                    / slow
                )
                * 100
            )


    # ------------------------------------------------------------
    # 1000-DAY PERCENT RANK
    # ------------------------------------------------------------

    rank = (
        percent_rank_current(
            ppo_b,
            1000
        )
    )

    if rank is None:

        return {
            "symbol":
                symbol,

            "signal":
                "INSUFFICIENT_HISTORY",

            "date":
                latest_date
        }


    pct_rank_b = (
        rank * -1
    )


    # ------------------------------------------------------------
    # ACCUMULATOR SIGNAL
    # ------------------------------------------------------------

    if pct_rank_b <= -95:

        signal = (
            "STRONG_BUY"
        )

    elif pct_rank_b <= -85:

        signal = (
            "BUY"
        )

    else:

        signal = (
            "NONE"
        )


    return {
        "symbol":
            symbol,

        "signal":
            signal,

        "date":
            latest_date,

        "close":
            str(
                latest["c"]
            )
    }


# ================================================================
# RUN SCANNER
# ================================================================

results = []

try:

    print(
        "Downloading Alpaca market data..."
    )

    print(
        f"Scanning {len(TICKERS)} unique tickers..."
    )

    all_bars = (
        download_all_bars()
    )

    print(
        "Download complete."
    )

    reference_date = (
        get_reference_date(
            all_bars
        )
    )

    print(
        f"Freshest market date: "
        f"{reference_date}"
    )


    for ticker in TICKERS:

        try:

            result = (
                get_signal(
                    ticker,
                    all_bars.get(
                        ticker,
                        []
                    ),
                    reference_date
                )
            )

            results.append(
                result
            )

            print(
                result
            )


        except Exception as e:

            result = {
                "symbol":
                    ticker,

                "signal":
                    "ERROR",

                "message":
                    str(e)
            }

            results.append(
                result
            )

            print(
                result
            )


except Exception as e:

    raise RuntimeError(
        f"Alpaca data download "
        f"failed: {e}"
    )


# ================================================================
# SAVE JSON
# ================================================================

with open(
    "signals.json",
    "w"
) as f:

    json.dump(
        results,
        f,
        indent=2
    )


# ================================================================
# SUMMARY
# ================================================================

summary = {}

for result in results:

    signal = (
        result["signal"]
    )

    summary[signal] = (
        summary.get(
            signal,
            0
        )
        + 1
    )


print("")
print(
    "SCAN SUMMARY"
)
print(
    "------------"
)


for signal, count in sorted(
    summary.items()
):

    print(
        f"{signal}: {count}"
    )


print("")
print(
    f"Finished. Scanned "
    f"{len(results)} tickers."
)
