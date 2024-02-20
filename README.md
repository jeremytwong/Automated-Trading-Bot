# Binance Automated Trading Bot

This project is an automated trading bot for the Binance cryptocurrency exchange. It uses the Binance API to place buy and sell orders based on the Double Exponential Moving Average (DEMA) of the cryptocurrency's price.

## Setup

Before you can use this bot, you need to get an API key and secret from Binance. Once you have these, you can add them to the `BinanceClient` class in the `main.py` file:


## Features

- Fetches historical klines (candlestick) data from Binance
- Calculates the Exponential Moving Average (EMA) and Double Exponential Moving Average (DEMA) of the price data
- Places buy orders when the price is above the DEMA by a certain threshold
- Places sell orders when the price is below the DEMA
- Checks for open orders
- Cancels orders
- Backtests the trading strategy on historical data
- Optimizes the trading strategy by finding the best window and threshold values

