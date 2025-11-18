# 📁 Full GitHub Project — Resco Meter (Risk‑O‑Meter)

Below is a complete GitHub‑ready project with **three files**:

* `app.py` — Streamlit application
* `requirements.txt` — Dependencies for Streamlit Cloud
* `README.md` — Project documentation

You can copy all files exactly into a new repository.

---

## 📌 `app.py`

```python
import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(layout="wide", page_title="Resco Meter - Risk-o-Meter")

# ------------ Helper Functions ------------
def safe_get(info, key, default=np.nan):
    return info.get(key, default) if isinstance(info, dict) else default


def score_from_bounds(value, bounds, invert=False):
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return np.nan
    low, high = bounds
    frac = (value - low) / (high - low)
    frac = np.clip(frac, 0, 1)
    score = frac * 100
    return 100 - score if invert else score


def compute_layers(ticker, period='2y'):
    tk = yf.Ticker(ticker)
    try:
        info = tk.info
    except:
        info = {}

    try:
        hist = tk.history(period=period, auto_adjust=True)
    except:
        hist = pd.DataFrame()

    layers = {}

    # 1) Volatility Risk
    vol = np.nan
    if not hist.empty:
        daily = hist['Close'].pct_change().dropna()
        vol = daily.std() * np.sqrt(252)
    layers['Volatility Risk'] = score_from_bounds(vol, (0.05, 1.2))

    # 2) Beta Risk
    beta = safe_get(info, 'beta', np.nan)
    layers['Market Risk (Beta)'] = score_from_bounds(beta, (0, 3))

    # 3) Liquidity Risk
    avg_vol = safe_get(info, 'averageVolume', np.nan)
    shares = safe_get(info, 'sharesOutstanding', np.nan)

    liq = avg_vol / shares if avg_vol and shares else np.nan
    layers['Liquidity Risk'] = score_from_bounds(liq, (1e-6, 0.05), invert=True)

    # 4) Leverage Risk
    de = safe_get(info, 'debtToEquity', np.nan)
    layers['Leverage Risk'] = score_from_bounds(de, (0, 400))

    # 5) Profitability Risk (ROE)
    roe = safe_get(info, 'returnOnEquity', np.nan)
    roe = roe * 100 if roe else np.nan
    layers['Profitability Risk'] = score_from_bounds(roe, (-50, 50), invert=True)

    # 6) Valuation Risk
    pe = safe_get(info, 'trailingPE', np.nan)
    layers['Valuation Risk'] = score_from_bounds(pe, (0, 100))

    # Overall Risk Average
    vals = [v for v in layers.values() if not np.isnan(v)]
    overall = np.mean(vals) if vals else 50

    return layers, overall, info


# ------------ UI Section ------------
st.title("📊 Resco Meter — Stock Risk-O-Meter")
st.write("Enter any stock ticker to analyze six layers of risk.")

ticker = st.text_input("Enter Stock Ticker (e.g., AAPL, TCS.NS)", "AAPL").upper()
period = st.selectbox("Select History Period", ["1y", "2y", "3y", "5y"], index=1)

if ticker:
    with st.spinner("Fetching data..."):
        layers, overall, info = compute_layers(ticker, period)

    # Stock Summary
    st.subheader(f"{info.get('shortName', ticker)} — {ticker}")
    st.write(f"Sector: {info.get('sector', 'NA')} | Industry: {info.get('industry', 'NA')}")

    # Overall Gauge
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = float(overall),
        title = {'text': "Overall Risk Score"},
        gauge = {
            'axis': {'range': [0, 100]},
            'bar': {'color': 'black'},
            'steps': [
                {'range': [0, 33], 'color': '#2ecc71'},
                {'range': [33, 66], 'color': '#f1c40f'},
                {'range': [66, 100], 'color': '#e74c3c'}
            ]
        }
    ))
    st.plotly_chart(fig, use_container_width=True)

    # Layer Breakdown
    st.subheader("Risk Layer Breakdown")
    cols = st.columns(3)
    i = 0
    for name, score in layers.items():
        with cols[i % 3]:
            st.metric(name, f"{score:.1f}" if not np.isnan(score) else "NA")
            st.progress(int(np.clip(score if not np.isnan(score) else 50, 0, 100)))
        i += 1

    # Key Info Table
    st.subheader("Key Stock Information")
    df = pd.DataFrame(list(info.items()), columns=["Key", "Value"])
    st.dataframe(df)

    # Price Chart
    try:
        hist = yf.Ticker(ticker).history(period=period, auto_adjust=True)
        st.subheader("Price History Chart")
        st.line_chart(hist['Close'])
    except:
        pass

st.caption("This tool is for educational purposes only. Always research before investing.")
```

---

## 📌 `requirements.txt`

```
streamlit
yfinance
pandas
numpy
plotly
scikit-learn
```

---

## 📌 `README.md`

```markdown
# 📊 Resco Meter — Risk-O-Meter (Streamlit)
A powerful Streamlit-based stock risk analysis tool that displays **six layers of risk** and an **overall risk score** using real-time data from Yahoo Finance.

## 🚀 Features
- Six risk layers:
  - Volatility Risk
  - Market Risk (Beta)
  - Liquidity Risk
  - Leverage Risk
  - Profitability Risk (ROE)
  - Valuation Risk (PE)
- Overall Risk Gauge (0–100)
- Auto-fetch stock info using yfinance
- Price History Chart
- Clean, mobile-friendly UI

## 📂 Project Structure
```

📁 project
┣ 📄 app.py
┣ 📄 requirements.txt
┗ 📄 README.md

````

## ▶️ Run Locally
```bash
pip install -r requirements.txt
streamlit run app.py
````

## ☁️ Deploy on Streamlit Cloud

1. Push all files to GitHub
2. Go to [https://share.streamlit.io](https://share.streamlit.io)
3. Select your repo → deploy → done!

## 📌 Notes

* This tool is for **educational and research** purposes only.
* Market data accuracy depends on Yahoo Finance.

```

---

If you want, I can also generate:
✅ `.gitignore`
✅ Better UI theme version
✅ Advanced AI scoring model

Just tell me!

```
