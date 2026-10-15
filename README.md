# Liquidity Sweep — 1 year tested on Gold and Nasdaq (Edge or Myth, Video 11)

Claim tested: "trade the liquidity sweep" — price pokes through an obvious high/low where stop losses sit, closes back inside, and reverses.

## Data
- Gold (XAUUSD) and Nasdaq 100 (US100), Dukascopy 1-minute history, resampled to 5-minute candles
- Test period: 1 Oct 2025 – 30 Sep 2026 (October 2026 shown separately in the video)
- $100 risked on every trade, no spread (same assumption for both versions)

## Rules (bt.py)
1. Levels: obvious swing highs/lows (pivot, 5 candles each side) from the last 2 days
2. Sweep: a 5-minute candle pierces the level and closes back inside
3. Entry: price breaks the sweep candle (low for a short, high for a long) within 3 candles
4. Stop: just beyond the sweep wick. Target: 3x the risk. Any open trade closes at 21:00 UTC
5. Sessions: Gold 07:00–20:00 UTC, Nasdaq 13:30–20:00 UTC
6. Trend filter: trade only in the direction of the 50 EMA — 1-hour in the original, 4-hour in the fix

## Results ($100 risk per trade)
| Version | Trades | Win rate | Profit factor | Total |
|---|---|---|---|---|
| Gold original (1H trend) | 480 | 35% | 1.36 | +$11,074 |
| Gold fixed (4H trend) | 350 | 39% | 1.67 | +$14,136 |
| Nasdaq original | 223 | 30% | 0.97 | −$414 |
| Nasdaq fixed | 176 | 37% | 1.43 | +$4,381 |

Gold fixed, by quarter: Q4 2025 +$5,737 · Q1 2026 +$3,105 · Q2 2026 +$5,925 · Q3 2026 −$630
Worst drawdown (gold fixed): −$1,512. October 2026 (1–13 Oct, outside the test): 10 trades, 2 winners, −$582.

Sit-out filters tested for Q3 (both rejected): skip when the 4-hour trend flipped too often (lowered total), monthly stop after −$500 (+$50, no real change).

## Files
- data.py — loads and resamples the data
- bt.py — the backtest (`run(sym, htf='1h'|'4h', ...)`)
- fix.py — runs the versions compared in the video
- trades_GOLD_original.csv, trades_GOLD_fix.csv, trades_NQ_original.csv, trades_NQ_fix.csv — every trade

Charts in the video are real TradingView (OANDA) charts; OANDA prices can differ from Dukascopy by $1–2.
Backtest results are hypothetical. Education only, not financial advice.
