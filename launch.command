#!/bin/bash
cd ~/Desktop/"ETH Dashboard"
echo "Starting ETH Dashboard..."
python3 -m streamlit run eth_arb_dashboard.py
read -p "Press enter to close..."