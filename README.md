# ETH Arbitrage Dashboard

A Streamlit app for analyzing ETH arbitrage opportunities across exchanges.

## Features
- Editable exchange price table
- Automatic best buy/sell route detection
- Net profit calculation after fees and slippage
- Comparison table for all exchange pairs
- One-click macOS launcher with `launch.command`

## Run locally

```bash
pip3 install -r requirements.txt
python3 -m streamlit run eth_arb_dashboard.py