import pandas as pd
import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import textwrap
import streamlit.components.v1 as components

st.set_page_config(page_title="Krischan Score Web-App", layout="wide")
st.title("Krischan Score: EMA20 + RSI + Momentum")
st.caption("Lern-Tool. Keine Finanzberatung. Das Tool bewertet nur nach deinen Regeln und garantiert keine Gewinne.")

DEFAULT_WATCHLIST = "QQQ, AAPL, NVDA, MU, PLD, BTC-USD, ETH-USD"

NASDAQ_100 = [
    "AAPL","ABNB","ADBE","ADI","ADP","ADSK","AEP","ALNY","AMAT","AMD",
    "AMGN","APP","ARM","ASML","AVGO","AXON","BKNG","CCEP","CHTR","CMCSA",
    "COST","CPRT","CRWD","CSCO","CSGP","CSX","CTAS","DASH","DDOG","DXCM",
    "EA","EXC","FANG","FAST","FER","FTNT","GEHC","GFS","GILD","GOOG",
    "GOOGL","HON","IDXX","INTC","INTU","ISRG","KDP","KHC","KLAC","LIN",
    "LRCX","MAR","MCHP","MDB","MDLZ","MELI","META","MNST","MRVL","MSFT",
    "MSTR","MU","NFLX","NVDA","NXPI","ODFL","ORLY","PANW","PAYX","PCAR",
    "PDD","PEP","PYPL","QCOM","REGN","ROP","ROST","SBUX","SHOP","SNDK",
    "SNPS","STX","TEAM","TMUS","TSLA","TTD","TTWO","TXN","VRSK","VRTX",
    "WBD","WDAY","WMT","XEL","ZS"
]

DAX_40 = [
    "ADS.DE","AIR.DE","ALV.DE","BAS.DE","BAYN.DE","BEI.DE","BMW.DE",
    "BNR.DE","CBK.DE","CON.DE","DB1.DE","DBK.DE","DHL.DE","DTE.DE",
    "DTG.DE","EOAN.DE","FRE.DE","HEN3.DE","HEI.DE","HNR1.DE","HOT.DE",
    "IFX.DE","MBG.DE","MRK.DE","MTX.DE","MUV2.DE","P911.DE","QIA.DE",
    "RHM.DE","RWE.DE","SAP.DE","SRT3.DE","SIE.DE","SHL.DE","ENR.DE",
    "SY1.DE","VNA.DE","VOW3.DE","ZAL.DE"
]

SP100 = [
    "AAPL","MSFT","NVDA","AMZN","META","GOOGL","GOOG","BRK-B",
    "LLY","JPM","V","MA","AVGO","XOM","UNH","COST","HD","PG",
    "JNJ","ABBV","MRK","PEP","KO","BAC","WMT","CRM","AMD",
    "NFLX","ADBE","LIN","ORCL","TMO","CVX","ACN","CSCO",
    "MCD","DHR","ABT","TXN","QCOM","INTU","AMGN","CAT",
    "IBM","GE","GS","RTX","LOW","ISRG","BKNG","BLK",
    "SCHW","SPGI","SYK","MDT","ELV","VRTX","PLD","ADI",
    "MU","PANW","LRCX","KLAC","SNPS","CDNS","CRWD","ABNB",
    "UBER","SHOP","ARM","MELI","PGR","MMC","CI","CMCSA",
    "TJX","C","USB","SO","DUK","AEP","MO","PM",
    "GILD","REGN","MAR","ADP","CSX","ETN","PH","WM",
    "APD","ECL","NKE","TGT","FIS","FICO","MS","AXP"
]

CRYPTO = [
    "BTC-USD","ETH-USD","SOL-USD","BNB-USD","XRP-USD","ADA-USD",
    "DOGE-USD","AVAX-USD","LINK-USD","DOT-USD"
]


@st.cache_data(ttl=86400)
def get_nasdaq_100() -> list[str]:
    try:
        tables = pd.read_html("https://en.wikipedia.org/wiki/Nasdaq-100")
        for df in tables:
            if "Ticker" in df.columns:
                return (
                    df["Ticker"]
                    .astype(str)
                    .str.replace(".", "-", regex=False)
                    .str.upper()
                    .tolist()
                )
    except Exception:
        pass
    return NASDAQ_100


@st.cache_data(ttl=86400)
def get_sp100() -> list[str]:
    return SP100


@st.cache_data(ttl=86400)
def get_dax_40() -> list[str]:
    try:
        tables = pd.read_html("https://en.wikipedia.org/wiki/DAX")
        for df in tables:
            if "Ticker" in df.columns:
                return (
                    (df["Ticker"].astype(str) + ".DE")
                    .str.replace("..DE", ".DE", regex=False)
                    .tolist()
                )
    except Exception:
        pass
    return DAX_40


with st.sidebar:
    st.header("Einstellungen")

    scan_mode = st.radio(
        "Scan-Modus",
        ["Eigene Watchlist", "Nasdaq 100", "S&P 500", "DAX 40", "Krypto", "Alles scannen"],
    )

    tickers_text = st.text_area(
        "Eigene Ticker, getrennt durch Komma",
        DEFAULT_WATCHLIST,
    )

    period = st.selectbox("Zeitraum", ["3mo", "6mo", "1y", "2y"], index=2)
    interval = st.selectbox("Kerzen", ["1d", "1h", "4h"], index=0)

    buy_threshold = st.slider("Kaufalarm ab Score", 0, 30, 25)
    sell_threshold = st.slider("Warnsignal bis Score", 0, 30, 14)
    max_results = st.slider("Max. angezeigte Ergebnisse", 5, 100, 30)


def get_tickers() -> list[str]:
    own = [t.strip().upper() for t in tickers_text.split(",") if t.strip()]

    if scan_mode == "Eigene Watchlist":
        return own
    if scan_mode == "Nasdaq 100":
        return get_nasdaq_100()
    if scan_mode == "S&P 500":
        return get_sp100()
    if scan_mode == "DAX 40":
        return get_dax_40()
    if scan_mode == "Krypto":
        return CRYPTO

    return sorted(set(own + get_nasdaq_100() + get_sp100() + get_dax_40() + CRYPTO))


def display_ticker_name(ticker: str) -> str:
    return ticker.replace(".DE", "").replace("-USD", "")


def rsi(series: pd.Series, length: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.ewm(alpha=1 / length, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / length, adjust=False).mean()

    rs = avg_gain / avg_loss.replace(0, pd.NA)
    return 100 - (100 / (1 + rs))


@st.cache_data(ttl=3600)
def get_name(ticker: str) -> str:
    try:
        info = yf.Ticker(ticker).info
        return (
            info.get("longName")
            or info.get("shortName")
            or info.get("name")
            or ticker
        )
    except Exception:
        return ticker


@st.cache_data(ttl=900)
def load_data(ticker: str, period: str, interval: str) -> pd.DataFrame:
    data = yf.download(
        ticker,
        period=period,
        interval=interval,
        auto_adjust=True,
        progress=False,
    )

    if data.empty:
        return pd.DataFrame()

    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    return data.dropna()


def analyze(ticker: str):
    data = load_data(ticker, period, interval)

    if data.empty or len(data) < 60:
        return None, None

    data = data.copy()
    data["EMA20"] = data["Close"].ewm(span=20, adjust=False).mean()
    data["RSI14"] = rsi(data["Close"], 14)
    data["EMA20_slope"] = data["EMA20"] - data["EMA20"].shift(20)
    data["Dist_EMA20_%"] = (data["Close"] - data["EMA20"]) / data["EMA20"] * 100

    last = data.iloc[-1]
    prev20 = data.iloc[-21:-1]

    close = float(last["Close"])
    ema20 = float(last["EMA20"])
    rsi14 = float(last["RSI14"])
    dist = float(last["Dist_EMA20_%"])
    slope = float(last["EMA20_slope"])

    trend_score = 0
    entry_score = 0
    notes = []

    if slope > ema20 * 0.03:
        trend_score += 5
        notes.append("EMA20 steigt stark")
    elif slope > 0:
        trend_score += 3
        notes.append("EMA20 steigt leicht")
    else:
        notes.append("EMA20 fällt")

    if close > ema20:
        trend_score += 5
        notes.append("Kurs über EMA20")
    elif abs(dist) < 2:
        trend_score += 2
        notes.append("Kurs nahe EMA20")
    else:
        notes.append("Kurs unter EMA20")

    if close > float(prev20["Close"].max()) * 0.95:
        trend_score += 5
        notes.append("Nähe zum 20-Kerzen-Hoch")
    elif close > float(prev20["Close"].median()):
        trend_score += 2
        notes.append("Seitwärts / mittlere Stärke")
    else:
        notes.append("Fallender Trend")

    if 40 <= rsi14 <= 55:
        entry_score += 5
        notes.append("RSI Sweet Spot")
    elif 55 < rsi14 <= 65:
        entry_score += 3
        notes.append("RSI etwas hoch")
    elif 30 <= rsi14 < 40:
        entry_score += 2
        notes.append("RSI niedrig")
    else:
        notes.append("RSI ungünstig")

    if 0 <= dist <= 3:
        entry_score += 5
        notes.append("Perfekte EMA20-Nähe")
    elif 3 < dist <= 8:
        entry_score += 3
        notes.append("Etwas von EMA20 entfernt")
    else:
        notes.append("Zu weit von EMA20 entfernt")

    recent_high = float(data["High"].tail(20).max())
    distance_to_high = (recent_high - close) / recent_high * 100

    if distance_to_high <= 2:
        momentum = 5
    elif distance_to_high <= 5:
        momentum = 4
    elif distance_to_high <= 10:
        momentum = 3
    elif distance_to_high <= 15:
        momentum = 2
    elif distance_to_high <= 20:
        momentum = 1
    else:
        momentum = 0

    score = trend_score + entry_score + momentum

    if score >= buy_threshold:
        signal = "🟢 Kaufkandidat / Watchlist"
    elif score <= sell_threshold:
        signal = "🔴 Meiden / Verkauf prüfen"
    else:
        signal = "🟡 Beobachten"

    if score >= 28:
        category = "🏆 Perfekt"
    elif score >= 24:
        category = "🚀 Kaufkandidat"
    elif score >= 20:
        category = "👀 Watchlist"
    elif score >= 15:
        category = "⚠️ Schwach"
    else:
        category = "🔴 Meiden"

    result = {
        "Ticker": display_ticker_name(ticker),
        "YahooTicker": ticker,
        "Name": get_name(ticker),
        "Kurs": round(close, 2),
        "EMA20": round(ema20, 2),
        "Abstand EMA20 %": round(dist, 2),
        "RSI14": round(rsi14, 2),
        "Trend": int(trend_score),
        "Entry": int(entry_score),
        "Moment": int(momentum),
        "Score": int(score),
        "Kategorie": category,
        "Signal": signal,
        "Begründung": "; ".join(notes),
    }

    return result, data


def score_color(score: int) -> str:
    if score >= 28:
        return "#00aa00"
    if score >= 24:
        return "#66cc00"
    if score >= 20:
        return "#ffcc00"
    if score >= 15:
        return "#ff8800"
    return "#cc0000"


def make_html_table(df: pd.DataFrame) -> str:
    display_df = df.copy()
    display_df = display_df.drop(columns=["YahooTicker"], errors="ignore")

    for col in ["Kurs", "EMA20", "Abstand EMA20 %", "RSI14"]:
        if col in display_df.columns:
            display_df[col] = display_df[col].map(lambda x: f"{float(x):.2f}")

    if "Score" in display_df.columns:
        display_df["Score"] = display_df["Score"].apply(
            lambda x: (
                f'<span style="color:{score_color(int(x))}; '
                f'font-weight:bold; font-size:18px;">{int(x)}</span>'
            )
        )

    html = textwrap.dedent("""
    <style>
    table {
        width: 100%;
        border-collapse: collapse;
        font-size: 14px;
    }

    th {
        text-align: center !important;
        padding: 10px;
        background-color: #e6e6e6;
        color: black;
        font-weight: 700;
        border-bottom: 2px solid #b0b0b0;
        white-space: nowrap;
    }

    td {
        padding: 8px;
        border-bottom: 1px solid rgba(150,150,150,0.20);
    }

    td:nth-child(1),
    td:nth-child(2),
    td:nth-child(12),
    td:nth-child(13) {
        text-align: left;
    }

    td:nth-child(3),
    td:nth-child(4),
    td:nth-child(5),
    td:nth-child(6),
    td:nth-child(7),
    td:nth-child(8),
    td:nth-child(9),
    td:nth-child(10),
    td:nth-child(11) {
        text-align: center;
    }

    tr:nth-child(even) {
        background-color: rgba(255,255,255,0.03);
    }
    </style>
    """)

    html += display_df.to_html(index=False, escape=False)
    return html


tickers = get_tickers()
rows = []
charts = {}

with st.spinner(f"{len(tickers)} Werte werden gescannt..."):
    progress = st.progress(0)

    for i, ticker in enumerate(tickers):
        result, data = analyze(ticker)

        if result:
            rows.append(result)
            charts[ticker] = data

        progress.progress((i + 1) / len(tickers))

if not rows:
    st.warning("Keine Daten geladen. Prüfe die Ticker.")
    st.stop()

summary = (
    pd.DataFrame(rows)
    .sort_values(["Score", "Trend", "Entry", "Moment"], ascending=False)
    .head(max_results)
    .reset_index(drop=True)
)

st.subheader("Bewertung")

components.html(
    make_html_table(summary),
    height=700,
    scrolling=True
)
top = summary[
    (summary["Trend"] == 15) &
    (summary["Entry"] == 10) &
    (summary["Moment"] >= 4)
]

warn = summary[summary["Score"] <= sell_threshold]

col1, col2, col3 = st.columns(3)
col1.metric("Gescannt", len(rows))
col2.metric("Top-Setups", len(top))
col3.metric("Warnsignale", len(warn))

st.subheader("🏆 Top-Setups")
if top.empty:
    st.info("Aktuell keine Top-Setups gefunden.")
else:
    st.markdown(make_html_table(top), unsafe_allow_html=True)

st.subheader("Zum Chart springen")

if "selected_ticker" not in st.session_state:
    st.session_state.selected_ticker = summary.loc[0, "YahooTicker"]

cols = st.columns(min(4, len(summary)))

for i, row in summary.iterrows():
    with cols[i % len(cols)]:
        label = f"{row['Ticker']} · {row['Score']}/30"
        if st.button(label, key=f"open_{row['YahooTicker']}", use_container_width=True):
            st.session_state.selected_ticker = row["YahooTicker"]

selected = st.session_state.selected_ticker

if selected not in charts:
    selected = summary.loc[0, "YahooTicker"]
    st.session_state.selected_ticker = selected

data = charts[selected]
row = summary[summary["YahooTicker"] == selected].iloc[0]

st.markdown(
    f"## {row['Ticker']} · {row['Name']} · "
    f"{row['Score']}/30 Punkte · {row['Kategorie']}"
)
st.write(row["Signal"])
st.caption(row["Begründung"])

fig = go.Figure()
fig.add_trace(
    go.Candlestick(
        x=data.index,
        open=data["Open"],
        high=data["High"],
        low=data["Low"],
        close=data["Close"],
        name="Kurs",
    )
)
fig.add_trace(
    go.Scatter(
        x=data.index,
        y=data["EMA20"],
        mode="lines",
        name="EMA20",
    )
)

fig.update_layout(
    title=f"{row['Ticker']}: Kurs + EMA20",
    xaxis_rangeslider_visible=False,
    height=560,
)

st.plotly_chart(fig, use_container_width=True)

fig2 = go.Figure()
fig2.add_trace(
    go.Scatter(
        x=data.index,
        y=data["RSI14"],
        mode="lines",
        name="RSI14",
    )
)

fig2.add_hline(y=70, line_dash="dash")
fig2.add_hline(y=55, line_dash="dot")
fig2.add_hline(y=40, line_dash="dot")
fig2.add_hline(y=30, line_dash="dash")

fig2.update_layout(
    title=f"{row['Ticker']}: RSI14",
    height=300,
)

st.plotly_chart(fig2, use_container_width=True)

st.info(
    "Hinweis: Das Tool bewertet nur nach deinen EMA20-/RSI-/Momentum-Regeln. "
    "Es ist keine Finanzberatung und garantiert keine Gewinne."
)
