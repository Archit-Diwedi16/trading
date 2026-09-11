"""Liquidity-sweep strategy research logic.

The implementation uses only confirmed historical swing points and therefore
avoids using future candles to create a signal.
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class Candle:
    timestamp: object
    open: float
    high: float
    low: float
    close: float
    volume: float = 0.0


@dataclass(frozen=True)
class Swing:
    index: int
    price: float
    kind: str  # "high" or "low"


@dataclass(frozen=True)
class Signal:
    index: int
    side: str  # "long" or "short"
    level: float
    sweep_price: float
    close: float
    stop_price: float


def confirmed_swings(candles: List[Candle], left: int = 3, right: int = 3) -> List[Swing]:
    """Return confirmed swing highs/lows using a left/right window.

    A point is confirmed only after ``right`` candles have closed, preventing
    look-ahead bias when the resulting swing is used by a backtest.
    """
    if left < 1 or right < 1:
        raise ValueError("left and right must be >= 1")

    swings: List[Swing] = []
    for i in range(left, len(candles) - right):
        window = candles[i - left : i + right + 1]
        high = candles[i].high
        low = candles[i].low

        if high == max(c.high for c in window) and sum(c.high == high for c in window) == 1:
            swings.append(Swing(i, high, "high"))
        if low == min(c.low for c in window) and sum(c.low == low for c in window) == 1:
            swings.append(Swing(i, low, "low"))

    return swings


def liquidity_sweep_signals(
    candles: List[Candle],
    left: int = 3,
    right: int = 3,
    min_rejection_pct: float = 0.05,
    stop_buffer_pct: float = 0.02,
) -> List[Signal]:
    """Generate research signals after a prior swing level is swept.

    Long: price trades below a confirmed swing low, then closes back above it.
    Short: price trades above a confirmed swing high, then closes back below it.

    Percentages are expressed as percent, e.g. 0.05 means 0.05%.
    """
    if min_rejection_pct < 0 or stop_buffer_pct < 0:
        raise ValueError("percentage parameters must be non-negative")

    swings = confirmed_swings(candles, left, right)
    swings_by_index = {s.index: s for s in swings}
    active_highs: List[Swing] = []
    active_lows: List[Swing] = []
    signals: List[Signal] = []

    for i, candle in enumerate(candles):
        # A swing becomes usable only after its confirmation window has ended.
        if i in swings_by_index:
            s = swings_by_index[i]
            if s.kind == "high":
                active_highs.append(s)
            else:
                active_lows.append(s)

        # A level must be historical relative to the current candle.
        prior_lows = [s for s in active_lows if s.index < i]
        prior_highs = [s for s in active_highs if s.index < i]

        if prior_lows:
            level = prior_lows[-1]
            rejection = (candle.close - level.price) / level.price * 100
            if candle.low < level.price and candle.close > level.price and rejection >= min_rejection_pct:
                stop = candle.low * (1 - stop_buffer_pct / 100)
                signals.append(Signal(i, "long", level.price, candle.low, candle.close, stop))

        if prior_highs:
            level = prior_highs[-1]
            rejection = (level.price - candle.close) / level.price * 100
            if candle.high > level.price and candle.close < level.price and rejection >= min_rejection_pct:
                stop = candle.high * (1 + stop_buffer_pct / 100)
                signals.append(Signal(i, "short", level.price, candle.high, candle.close, stop))

    return signals
