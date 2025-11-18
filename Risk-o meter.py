"""
Streamlit Risk-o-Meter (Resco Meter)
File: streamlit_resco_meter.py

How to use:
1. Save this file to a repo on GitHub (e.g., main.py or streamlit_resco_meter.py).
2. Create a virtualenv and install requirements: `pip install -r requirements.txt` (requirements below).
3. Run locally: `streamlit run streamlit_resco_meter.py`.

Requirements (requirements.txt):
streamlit
yfinance
pandas
numpy
plotly
scikit-learn

This app fetches stock data via yfinance and computes six risk-layer scores (0-100):
 - Volatility Risk (price volatility)
 - Market Risk (beta)
 - Liquidity Risk (avg volume / shares outstanding)
 - Leverage Risk (debt-to-equity when available)
 - Profitability Risk (ROE — lower ROE increases risk)
 - Valuation Risk (trailing P/E vs. simple thresholds)

The app then shows each layer, an aggregated risk gauge (overall risk 0-100), and tabular key info.
Note: yfinance occasionally returns incomplete info for some tickers (especially OTC). The app handles missing values gracefully.
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from sklearn.preprocessing import minmax_scale
from datetime import datetime

st.set_page_config(layout="wide", page_title="Resco Meter - Risk-o-Meter")

# ---------- Helper scoring functions ----------

def safe_get(info, key, default=np.nan):
    return info.get(key, default) if isinstance(info, dict) else default


def score_from_bounds(value, bounds, invert=False):
    """Map a numeric value to 0-100 given bounds = (low, high).
    If invert=True then lower value => lower risk (so we invert mapping).
    Values outside bounds are clipped.
    """
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return np.nan
    low, high = bounds
    if high == low:
        return 50.0
    frac = (value - low) / (high - low)
    frac = np.clip(frac, 0, 1)
    score = frac * 100
    return 100 - score if invert else score


# ---------- Layer computations ----------

def compute_layers(ticker, period='3y'):
    t0 = datetime.now()
    tk = yf.Ticker(ticker)

    info = {}
    try:
        info = tk.info
    except Exception:
        info = {}

    # price history
    try:
        hist = tk.history(period=period, auto_adjust=True)
    except Exception:
        hist = pd.DataFrame()

    layers = {}

    # 1) Volatility Risk: annualized volatility of daily returns
    vol = np.nan
    if not hist.empty and 'Close' in hist.columns and len(hist) > 30:
        daily_ret = hist['Close'].pct_change().dropna()
        vol = daily_ret.std() * np.sqrt(252)
    # map vol to score: low=0.05, high=1.2 (5% to 120% ann vol)
    layers['Volatility Risk'] = score_from_bounds(vol, (0.05, 1.2), invert=False)

    # 2) Market Risk (Beta)
    beta = safe_get(info, 'beta', np.nan)
    # typical beta range: 0 to 3 -> map 0->0 risk, 3->100 risk
    layers['Market Risk (Beta)'] = score_from_bounds(beta, (0.0, 3.0), invert=False)

    # 3) Liquidity Risk: average volume relative to shares outstanding
    avg_vol = safe_get(info, 'averageVolume', np.nan)
    shares = safe_get(info, 'sharesOutstanding', np.nan)
    liquidity_ratio = np.nan
    if not np.isnan(avg_vol) and not np.isnan(shares) and shares > 0:
        liquidity_ratio = avg_vol / shares
    # liquidity: higher ratio -> *lower* risk (liquid = better). We'll invert mapping.
    # typical liquidity_ratio bounds 1e-6 (very illiquid) to 0.05 (extremely liquid)
    layers['Liquidity Risk'] = score_from_bounds(liquidity_ratio, (1e-6, 0.05), invert=True)

    # 4) Leverage Risk: debt to equity
    debt_eq = safe_get(info, 'debtToEquity', np.nan)
    # map 0->0 risk, 400->100 risk (a company with 400% debt/equity is risky)
    layers['Leverage Risk'] = score_from_bounds(debt_eq, (0.0, 400.0), invert=False)

    # 5) Profitability Risk: return on equity (ROE)
    roe = safe_get(info, 'returnOnEquity', np.nan)
    # returnOnEquity is often fractional (e.g., 0.18). Convert to percent
    if not np.isnan(roe):
        roe_pct = roe * 100
    else:
        roe_pct = np.nan
    # Higher ROE = lower risk. We'll invert mapping with bounds (-50% to 50%)
    layers['Profitability Risk'] = score_from_bounds(roe_pct, (-50.0, 50.0), invert=True)

    # 6) Valuation Risk: trailing PE
    pe = safe_get(info, 'trailingPE', np.nan)
    # PE: low PE often lower risk, but very low could be distress. We'll keep simple: 0->0, 100->100
    layers['Valuation Risk'] = score_from_bounds(pe, (0.0, 100.0), invert=False)

    # Gather key info values for display
    key_info = {
        'shortName': safe_get(info, 'shortName', ''),
        'longName': safe_get(info, 'longName', ''),
        'sector': safe_get(info, 'sector', ''),
        'industry': safe_get(info, 'industry', ''),
        'marketCap': safe_get(info, 'marketCap', np.nan),
        'currentPrice': safe_get(info, 'currentPrice', np.nan),
        'previousClose': safe_get(info, 'previousClose', np.nan),
        'volume': safe_get(info, 'volume', np.nan),
        'averageVolume': avg_vol,
        'beta': beta,
        'debtToEquity': debt_eq,
        'trailingPE': pe,
        'returnOnEquity': roe,
        'sharesOutstanding': shares,
    }

    # compute overall risk as weighted average (weights can be tuned)
    weights = {
        'Volatility Risk': 0.22,
        'Market Risk (Beta)': 0.18,
        'Liquidity Risk': 0.15,
        'Leverage Risk': 0.18,
        'Profitability Risk': 0.14,
        'Valuation Risk': 0.13,
    }

    # Replace NaN layer scores with the mean of available scores before aggregation
    scores = {}
    for k, v in layers.items():
        scores[k] = float(v) if not (isinstance(v, float) and np.isnan(v)) else np.nan

    available = [v for v in scores.values() if not np.isnan(v)]
    fallback = np.mean(available) if available else 50.0

    weighted_sum = 0.0
    weight_total = 0.0
    for k, w in weights.items():
        val = scores.get(k, np.nan)
        if np.isnan(val):
            val = fallback
        weighted_sum += val * w
        weight_total += w

    overall = weighted_sum / weight_total if weight_total > 0 else 50.0

    # small historical summary
    hist_summary = None
    if not hist.empty:
        hist_summary = {
            'first_date': str(hist.index.min().date()),
            'last_date': str(hist.index.max().date()),
            'price_change_pct': (hist['Close'].iloc[-1] / hist['Close'].iloc[0] - 1) * 100 if len(hist) > 0 else np.nan,
            'annualized_vol': vol,
        }

    return {
        'layers': scores,
        'overall': overall,
        'key_info': key_info,
        'hist_summary': hist_summary,
        'raw_info': info,
    }


# ---------- UI ----------

st.title("Resco Meter — Stock Risk-o-Meter")
st.markdown("Enter a stock ticker (e.g., AAPL, MSFT, TCS.NS) and the app will evaluate six risk layers and show an overall risk score.")

col1, col2 = st.columns([1, 3])
with col1:
    ticker_input = st.text_input("Ticker symbol", value="AAPL")
    period = st.selectbox("History period for volatility", options=['1y', '2y', '3y', '5y'], index=2)
    refresh = st.button("Analyze")

with col2:
    st.empty()

if ticker_input:
    ticker = ticker_input.strip().upper()
    with st.spinner(f"Fetching data for {ticker}..."):
        result = compute_layers(ticker, period=period)

    key = result['key_info']

    # top summary
    left, right = st.columns([2, 1])
    with left:
        st.subheader(f"{key.get('shortName') or ticket if (ticket:=ticker)} — {ticker}")
        st.write(f"Sector: {key.get('sector')} | Industry: {key.get('industry')}")
        prices = f"Price: {key.get('currentPrice')} | Prev Close: {key.get('previousClose')} | Market Cap: {key.get('marketCap')}"
        st.write(prices)

    # Overall gauge
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = float(result['overall']),
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': f"Overall Risk (0 low - 100 high)"},
        gauge = {
            'axis': {'range': [0, 100]},
            'bar': {'color': "black"},
            'steps': [
                {'range': [0, 33], 'color': "#2ecc71"},
                {'range': [33, 66], 'color': "#f1c40f"},
                {'range': [66, 100], 'color': "#e74c3c"},
            ],
        }
    ))
    fig.update_layout(height=300, margin=dict(l=20, r=20, t=40, b=20))
    with right:
        st.plotly_chart(fig, use_container_width=True)

    # show layer breakdown
    st.subheader("Layer breakdown")
    layers = result['layers']
    cols = st.columns(3)
    i = 0
    for layer_name, score in layers.items():
        col = cols[i % 3]
        with col:
            sc = score if not np.isnan(score) else None
            st.metric(layer_name, f"{sc:.1f}" if sc is not None else "N/A")
            st.progress(int(np.clip(sc if sc is not None else 50, 0, 100)))
        i += 1

    # show key info table
    st.subheader("Key Info")
    ki = pd.DataFrame(list(result['key_info'].items()), columns=['Key', 'Value'])
    st.table(ki)

    # show historical plot
    try:
        hist = yf.Ticker(ticker).history(period=period, auto_adjust=True)
        if not hist.empty:
            st.subheader("Price history")
            st.line_chart(hist['Close'])
    except Exception:
        pass

    # show raw info (collapsible)
    with st.expander("Show raw data returned by yfinance (debug)"):
        st.json(result['raw_info'])

    st.caption("Risk scores are heuristic and for informational/educational use only. Always do your own research before making investment decisions.")

# End of file
