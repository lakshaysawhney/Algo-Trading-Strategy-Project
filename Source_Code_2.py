from blueshift.library.technicals.indicators import bollinger_band, doji, rsi, ema, atr, macd
from blueshift.finance import commission, slippage
from blueshift.api import(  symbol,
                            order_target_percent,
                            set_commission,
                            set_slippage,
                            schedule_function,
                            date_rules,
                            time_rules,
                       )

def initialize(context):
    # Universe selection
    context.securities = [symbol('MSFT'), symbol('GOOG')]

    # Strategy parameters
    context.params = {
        'indicator_lookback': 150,
        'indicator_freq': '1m',
        'buy_signal_threshold': 0.25,
        'sell_signal_threshold': -0.25,
        'BBands_period': 15,
        'RSI_period': 14,
        'MACD_fast': 12,
        'MACD_slow': 26,
        'MACD_signal': 9,
        'trade_freq': 5,
        'leverage': 1.25,
        'stop_loss_pct': 0.02,
        'take_profit_pct': 0.03
    }

    # Variables to track signals and portfolio
    context.signals = dict((security, 0) for security in context.securities)
    context.target_position = dict((security, 0) for security in context.securities)
    context.entry_prices = dict((security, None) for security in context.securities)

    # Set trading cost and slippage
    set_commission(commission.PerShare(cost=0.0, min_trade_cost=0.0))
    set_slippage(slippage.FixedSlippage(0.00))

    # Schedule functions
    freq = int(context.params['trade_freq'])
    schedule_function(run_strategy, date_rules.every_day(), time_rules.every_nth_minute(freq))
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
    num_secs = len(context.securities)
    for security in context.securities:
        atr_value = atr(data.history(security, ['high', 'low', 'close'], 20, '1d'), 14)
        weight = 0.05 / atr_value  # Dynamic position sizing
        if context.signals[security] > context.params['buy_signal_threshold']:
            context.target_position[security] = weight * context.params['leverage']
        elif context.signals[security] < context.params['sell_signal_threshold']:
            context.target_position[security] = -weight * context.params['leverage']
        else:
            context.target_position[security] = 0

def generate_signals(context, data):
    try:
        price_data = data.history(context.securities, ['open', 'high', 'low', 'close'], 
                                  context.params['indicator_lookback'], context.params['indicator_freq'])
    except Exception as e:
        print(f"Data history error: {e}")
        return

    for security in context.securities:
        px = price_data.xs(security)
        context.signals[security] = signal_function(px, context.params)

def signal_function(px, params):
    ind1 = doji(px)
    upper, mid, lower = bollinger_band(px.close.values, params['BBands_period'])
    rsi_value = rsi(px.close.values, params['RSI_period'])
    macd_line, signal_line, _ = macd(px.close.values, params['MACD_fast'], params['MACD_slow'], params['MACD_signal'])

    if upper - lower == 0:
        return 0

    last_px = px.close.values[-1]
    dist_to_upper = 100 * (upper - last_px) / (upper - lower)

    if ind1 > 0 and dist_to_upper < 30 and rsi_value < 30:
        return 1
    elif ind1 > 0 and dist_to_upper > 70 and rsi_value > 70:
        return -1
    elif macd_line > signal_line:
        return 1
    elif macd_line < signal_line:
        return -1
    else:
        return 0
