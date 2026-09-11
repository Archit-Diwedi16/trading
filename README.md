# Trading Strategy Research

## V1: Liquidity Sweep + Swing High/Low

This repository contains a research/backtesting implementation of a price-action strategy built around recent swing highs/lows and liquidity sweeps.

### Initial design
- Detect confirmed swing highs and swing lows from OHLCV data.
- Track recent structural levels without look-ahead bias.
- Detect a sweep when price trades beyond a prior swing level and then closes back through the level.
- Require configurable rejection distance and confirmation candles.
- Generate long/short research signals only; no live order execution.
- Include configurable risk management and position sizing for a ₹50,000 reference account.

### Important
This is a research system. Backtest results are not evidence of future profitability. Validate with realistic costs, slippage, and out-of-sample data before considering live use.
