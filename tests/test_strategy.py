from trading.strategy import Candle, confirmed_swings, liquidity_sweep_signals


def test_confirmed_swing_high_and_low():
    candles = [
        Candle(i, 10, h, 10, 10) for i, h in enumerate([11, 12, 15, 13, 12, 10])
    ]
    candles[3] = Candle(3, 13, 13, 9, 10)
    candles[4] = Candle(4, 12, 12, 8, 9)
    swings = confirmed_swings(candles, left=1, right=1)
    assert any(s.index == 2 and s.kind == "high" for s in swings)
    assert any(s.index == 4 and s.kind == "low" for s in swings)


def test_long_liquidity_sweep():
    candles = [
        Candle(i, 100, h, l, c) for i, (h, l, c) in enumerate([
            (101, 99, 100),
            (102, 98, 101),
            (103, 97, 102),
            (102, 98, 100),
            (101, 95, 100.20),
        ])
    ]
    signals = liquidity_sweep_signals(candles, left=1, right=1, min_rejection_pct=0.05)
    assert any(s.side == "long" and s.index == 4 for s in signals)
