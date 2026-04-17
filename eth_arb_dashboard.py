import streamlit as st
import pandas as pd
from dataclasses import dataclass

st.set_page_config(page_title="ETH Arbitrage Dashboard", layout="wide")


@dataclass
class Fees:
    buy_fee_pct: float
    sell_fee_pct: float
    slippage_pct: float


def calculate_arbitrage(buy_price: float, sell_price: float, eth_amount: float, fees: Fees) -> dict:
    gross_cost = buy_price * eth_amount
    gross_revenue = sell_price * eth_amount

    buy_fee = gross_cost * (fees.buy_fee_pct / 100)
    sell_fee = gross_revenue * (fees.sell_fee_pct / 100)
    slippage_cost = (gross_cost + gross_revenue) * (fees.slippage_pct / 100)

    total_cost = gross_cost + buy_fee
    total_revenue = gross_revenue - sell_fee
    net_profit = total_revenue - total_cost - slippage_cost

    return {
        "gross_cost": gross_cost,
        "gross_revenue": gross_revenue,
        "buy_fee": buy_fee,
        "sell_fee": sell_fee,
        "slippage_cost": slippage_cost,
        "net_profit": net_profit,
    }


def format_money(value: float) -> str:
    return f"${value:,.2f}"


st.title("💰 ETH Arbitrage Dashboard")
st.caption("Analyze ETH price differences across exchanges and estimate net profit after fees and slippage.")

st.markdown("---")

left, right = st.columns([1, 2])

with left:
    st.subheader("Trade Settings")

    eth_amount = st.number_input("ETH Amount", min_value=0.01, value=1.00, step=0.1)

    st.markdown("**Fee Assumptions**")
    buy_fee_pct = st.number_input("Buy Fee %", min_value=0.0, value=0.10, step=0.01)
    sell_fee_pct = st.number_input("Sell Fee %", min_value=0.0, value=0.10, step=0.01)
    slippage_pct = st.number_input("Slippage %", min_value=0.0, value=0.05, step=0.01)

    st.markdown("---")
    st.markdown("**Notes**")
    st.write("- Buy low on one exchange")
    st.write("- Sell high on another")
    st.write("- Net profit accounts for fees and slippage")

with right:
    st.subheader("Exchange Prices")

    default_prices = pd.DataFrame(
        {
            "Exchange": ["Binance", "Coinbase", "Kraken", "Gemini"],
            "ETH Price (USD)": [1885.00, 1910.00, 1897.50, 1903.25],
        }
    )

    edited_prices = st.data_editor(
        default_prices,
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True,
    )

fees = Fees(
    buy_fee_pct=buy_fee_pct,
    sell_fee_pct=sell_fee_pct,
    slippage_pct=slippage_pct,
)

clean_prices = edited_prices.copy()
clean_prices["Exchange"] = clean_prices["Exchange"].astype(str).str.strip()

clean_prices = clean_prices[
    (clean_prices["Exchange"] != "") &
    (clean_prices["ETH Price (USD)"].notna())
]

if len(clean_prices) < 2:
    st.warning("Please provide at least two exchanges to compare.")
    st.stop()

records = clean_prices.to_dict("records")
opportunities = []

for buy in records:
    for sell in records:
        if buy["Exchange"] == sell["Exchange"]:
            continue

        result = calculate_arbitrage(
            buy_price=float(buy["ETH Price (USD)"]),
            sell_price=float(sell["ETH Price (USD)"]),
            eth_amount=eth_amount,
            fees=fees,
        )

        opportunities.append(
            {
                "Buy Exchange": buy["Exchange"],
                "Sell Exchange": sell["Exchange"],
                "Buy Price": float(buy["ETH Price (USD)"]),
                "Sell Price": float(sell["ETH Price (USD)"]),
                "Spread": float(sell["ETH Price (USD)"]) - float(buy["ETH Price (USD)"]),
                "Gross Cost": result["gross_cost"],
                "Gross Revenue": result["gross_revenue"],
                "Buy Fee": result["buy_fee"],
                "Sell Fee": result["sell_fee"],
                "Slippage Cost": result["slippage_cost"],
                "Net Profit": result["net_profit"],
            }
        )

results_df = pd.DataFrame(opportunities).sort_values("Net Profit", ascending=False).reset_index(drop=True)

best = results_df.iloc[0]

st.markdown("---")
st.subheader("Best Opportunity")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Buy On", best["Buy Exchange"])
c2.metric("Sell On", best["Sell Exchange"])
c3.metric("Spread", format_money(best["Spread"]))
c4.metric("Net Profit", format_money(best["Net Profit"]))

if best["Net Profit"] > 0:
    st.success(
        f"Best route: Buy on {best['Buy Exchange']} at {format_money(best['Buy Price'])} "
        f"and sell on {best['Sell Exchange']} at {format_money(best['Sell Price'])}. "
        f"Estimated net profit: {format_money(best['Net Profit'])}."
    )
else:
    st.error(
        f"No profitable opportunity found after fees and slippage. "
        f"Best current result: {format_money(best['Net Profit'])}."
    )

st.markdown("---")
st.subheader("All Arbitrage Comparisons")

display_df = results_df.copy()
money_columns = [
    "Buy Price",
    "Sell Price",
    "Spread",
    "Gross Cost",
    "Gross Revenue",
    "Buy Fee",
    "Sell Fee",
    "Slippage Cost",
    "Net Profit",
]

for col in money_columns:
    display_df[col] = display_df[col].map(format_money)

st.dataframe(display_df, use_container_width=True, hide_index=True)

st.markdown("---")
st.subheader("Profitability Breakdown")

profitable_count = int((results_df["Net Profit"] > 0).sum())
unprofitable_count = int((results_df["Net Profit"] <= 0).sum())

p1, p2, p3 = st.columns(3)
p1.metric("Total Routes Checked", len(results_df))
p2.metric("Profitable Routes", profitable_count)
p3.metric("Unprofitable Routes", unprofitable_count)

with st.expander("How net profit is calculated"):
    st.write(
        """
        Net Profit = Gross Revenue
        - Sell Fee
        - Gross Cost
        - Buy Fee
        - Slippage Cost
        """
    )