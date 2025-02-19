from blueshift.library.technicals.indicators import bollinger_band, doji, macd, atr, adx
from blueshift.finance import commission, slippage
from blueshift.api import (
    symbol,
    order_target_percent,
    set_commission,
    set_slippage,
    schedule_function,
    date_rules,
    time_rules,
)

def initialize(context):
    context.securities = [symbol('MSFT'), symbol('GOOG'), symbol('AAPL'), symbol('AMZN'), symbol('TSLA')]

    context.params = {
        'indicator_lookback': 200,
        'indicator_freq': '1m',
        'BBands_period': 20,
        'MACD_fast': 12,
        'MACD_slow': 26,
        'MACD_signal': 9,
        'trade_freq': 2,  # Execute every 2 minutes
        'stop_loss_pct': 0.15,
        'take_profit_pct': 0.25,
        'leverage': 2,
        'volume_threshold': 1.5,  # Multiplier for average volume
    }

    context.signals = dict((security, 0) for security in context.securities)
    context.target_position = dict((security, 0) for security in context.securities)
    context.entry_prices = dict((security, None) for security in context.securities)

    set_commission(commission.PerShare(cost=0.0, min_trade_cost=0.0))
    set_slippage(slippage.FixedSlippage(0.00))

    schedule_function(run_strategy, date_rules.every_day(), time_rules.every_nth_minute(context.params['trade_freq']))
    schedule_function(stop_trading, date_rules.every_day(), time_rules.market_close(minutes=30))

    context.trade = True

def before_trading_start(context, data):
    context.trade = True

def stop_trading(context, data):
    context.trade = False

def run_strategy(context, data):
    if not context.trade:
        return

    generate_signals(context, data)
    generate_target_position(context, data)
    rebalance(context, data)

def rebalance(context, data):
    for security in context.securities:
        target_weight = context.target_position[security]
        if context.entry_prices[security] is not None:
            current_price = data.current(security, 'close')
            # Stop Loss
            if current_price <= context.entry_prices[security] * (1 - context.params['stop_loss_pct']):
                order_target_percent(security, 0)
                context.entry_prices[security] = None
                continue
            # Take Profit
            if current_price >= context.entry_prices[security] * (1 + context.params['take_profit_pct']):
                order_target_percent(security, 0)
                context.entry_prices[security] = None
                continue
        order_target_percent(security, target_weight)
        if target_weight != 0:
            context.entry_prices[security] = data.current(security, 'close')

def generate_target_position(context, data):
    for security in context.securities:
        atr_value = atr(data.history(security, ['high', 'low', 'close'], 20, '1d'), 14)
        weight = min(max(0.2 / atr_value, 0.02), 0.3)  # Min weight 2%, max 30%
        if context.signals[security] > 0:
            context.target_position[security] = weight * context.params['leverage']
        elif context.signals[security] < 0:
            context.target_position[security] = -weight * context.params['leverage']
        else:
            context.target_position[security] = 0

def generate_signals(context, data):
    try:
        price_data = data.history(context.securities, ['open', 'high', 'low', 'close', 'volume'], 
                                  context.params['indicator_lookback'], context.params['indicator_freq'])
    except Exception as e:
        print(f"Data history error: {e}")
        return

    for security in context.securities:
        px = price_data.xs(security)
        context.signals[security] = signal_function(px, context.params)

def identify_patterns(px):
    """Identify candlestick patterns."""
    open_price = px.open.values[-1]
    close_price = px.close.values[-1]
    high_price = px.high.values[-1]
    low_price = px.low.values[-1]

    if abs(close_price - open_price) < (high_price - low_price) * 0.1:
        # Narrow body for Doji-like candles
        if (high_price - close_price) > 2 * (close_price - low_price):
            return "Gravestone Doji"
        elif (close_price - low_price) > 2 * (high_price - close_price):
            return "Dragonfly Doji"
    elif close_price > open_price and (close_price - low_price) > 2 * (high_price - close_price):
        return "Hammer"
    elif close_price < open_price and (high_price - close_price) > 2 * (close_price - low_price):
        return "Inverted Hammer"
    return None

def signal_function(px, params):
    """Generate trading signals based on patterns, volume, and indicators."""
    pattern = identify_patterns(px)
    upper, mid, lower = bollinger_band(px.close.values, params['BBands_period'])
    macd_line, signal_line, _ = macd(px.close.values, params['MACD_fast'], params['MACD_slow'], params['MACD_signal'])
    adx_value = adx(px.high.values, px.low.values, px.close.values, 14)
    avg_volume = px.volume.values[-params['indicator_lookback']:].mean()
    last_volume = px.volume.values[-1]

    if upper - lower == 0:
        return 0

    # Check for high volume confirmation
    if last_volume < params['volume_threshold'] * avg_volume:
        return 0

    last_px = px.close.values[-1]
    dist_to_upper = 100 * (upper - last_px) / (upper - lower)

    # Use ADX for trend strength filtering
    if adx_value < 15:
        return 0

    # Candlestick Patterns with volume confirmation
    if pattern == "Dragonfly Doji" and dist_to_upper < 30 and macd_line > signal_line:
        return 1  # Buy Signal
    elif pattern == "Gravestone Doji" and dist_to_upper > 70 and macd_line < signal_line:
        return -1  # Sell Signal
    elif pattern == "Hammer" and macd_line > signal_line:
        return 1  # Buy Signal
    elif pattern == "Inverted Hammer" and macd_line < signal_line:
        return -1  # Sell Signal
    else:
        return 0
    