import os

from bitmex import bitmex as Bitmex
from bravado.exception import HTTPError
from decimal import localcontext, Decimal, ROUND_HALF_UP

from mexpy.indicators import Williams
from mexpy.indicators import vwma

import time
import logging
import sys
import requests
import math

API_KEY = os.getenv('API_KEY', 'VVaTsmsM08lYOKOu663RmjOD')
API_SECRET = os.getenv('API_SECRET', 'EDiua09FY7r0tJyPkqbwHhTKeJgCbaX9lq40YhQ4V6ajHmr-')
USE_TESTNET = True if os.getenv('USE_TESTNET', '0') == '1' else False
TF = os.getenv('TF', '5m')
CONTRACTS = int(os.getenv('CONTRACTS', '10'))
LEVERAGE = int(os.getenv('LEVERAGE', '20'))
SYMBOL = 'XBTUSD'
REFRESH_TIME = int(os.getenv('REFRESH_TIME', 10))
DEBUG = os.getenv('DEBUG', '0')
TG_API_KEY = os.getenv('TG_API_KEY', '472836801:AAGQgDhB0dg471Nvqc9RjqiXZJ4K2qnieHQ')
TG_CHAT_ID = os.getenv('TG_CHAT_ID', '-1001351609280')
LIMIT_SELL_MARGIN = float(os.getenv('LIMIT_SELL_MARGIN', '40.0'))
STOP_MARGIN = float(os.getenv('STOP_MARGIN', '50.0'))
VWMA_PERIOD = int(os.getenv('VWMA_PERIOD', '34'))
GRACE_PERIOD_IN_MINUTES = int(os.getenv('GRACE_PERIOD_IN_MINUTES', '10'))

bitmex_client = Bitmex(test=USE_TESTNET,
                       api_key=API_KEY,
                       api_secret=API_SECRET)

LAST_ORDER_FRACTAL = 0.0


def setup_custom_logger(name):
    formatter = logging.Formatter(fmt='%(asctime)s - %(levelname)-2s - %(message)s',
                                  datefmt='%Y-%m-%d %H:%M:%S')

    screen_handler = logging.StreamHandler(stream=sys.stdout)
    screen_handler.setFormatter(formatter)

    lg = logging.getLogger(name)
    log_level = logging.DEBUG if DEBUG == '1' else logging.INFO
    lg.setLevel(log_level)
    lg.addHandler(screen_handler)

    return lg


logger = setup_custom_logger('mexpy')


def send_telegram_message(text):
    url = 'https://api.telegram.org/bot%s/sendMessage' % TG_API_KEY
    query = {
        'chat_id': TG_CHAT_ID,
        'text': text,
        'parse_mode': 'markdown',
    }

    r = requests.get(url,
                     params=query)
    result = r.json()

    return result


def construct_buy_telegram_message(market_order, fractal_price, vwma_price):
    message = '*Mexpy*\n\nMarket Buy Price: %.2f\nLimit Sell Price: %.2f\nStop Price: %.2f\n\nSymbol: %s\nTF: %s\nContracts: %d\nFractal Price: %.2f\nVWMA: %.2f'

    market_buy_price = market_order.get('avgPx')
    limit_sell_price = format_price(market_buy_price * 1.004)
    stop_price = format_price(market_buy_price * 0.996)

    message = message % (market_buy_price,
                         limit_sell_price,
                         stop_price,
                         SYMBOL,
                         TF,
                         CONTRACTS,
                         fractal_price,
                         vwma_price)

    return message


def construct_sell_telegram_message(market_order, fractal_price, vwma_price):
    message = '*Mexpy*\n\n*SOLD!*\n\nOpit Percentage: ~*%.2f*\n\nMarket Buy Price: %.2f\nLimit Sell Price: %.2f\nStop Price: %.2f\n\nSymbol: %s\nTF: %s\nContracts: %d\nFractal Price: %.2f\nVWMA: %.2f'

    market_buy_price = market_order.get('avgPx')
    limit_sell_price = format_price(market_buy_price * 1.004)
    stop_price = format_price(market_buy_price * 0.996)
    opit_percentage = (limit_sell_price / market_buy_price - 1.0) * LEVERAGE

    message = message % (opit_percentage,
                         market_buy_price,
                         limit_sell_price,
                         stop_price,
                         SYMBOL,
                         TF,
                         CONTRACTS,
                         fractal_price,
                         vwma_price)

    return message


def get_klines() -> list:
    candles = bitmex_client.Trade.Trade_getBucketed(binSize=TF,
                                                    symbol=SYMBOL,
                                                    reverse=True,
                                                    count=300).result()
    candles = candles[0] if len(candles) == 2 else []
    candles.reverse()

    return candles


def generate_fractals(klines: list) -> list:
    highs = list(map(lambda x: x.get('high'), klines))
    up_fractals = Williams.up_fractal(highs=highs)

    for index, item in enumerate(klines):
        klines[index].update({'up_fractal': up_fractals[index]})

    return klines


def generate_vwma(klines: list, period: int=20):
    closes = list(map(lambda x: x.get('close'), klines))
    volumes = list(map(lambda x: x.get('volume'), klines))
    vwmas = vwma(closes=closes,
                 volumes=volumes,
                 period=period)

    for index, item in enumerate(klines):
        klines[index].update({'vwma': vwmas[index]})

    return klines


def format_price(price):
    with localcontext() as ctx:
        ctx.rounding = ROUND_HALF_UP
        result = Decimal(price)

    return float(result)


def create_orders(current_price: float) -> tuple:
    logger.info('Going to long with last candle close of: %.2f @ %sx Leverage' % (current_price, LEVERAGE))
    bitmex_client.Position.Position_updateLeverage(symbol=SYMBOL,
                                                   leverage=LEVERAGE)
    market_buy_order = bitmex_client.Order.Order_new(symbol=SYMBOL,
                                                     orderQty=CONTRACTS,
                                                     displayQty=0,
                                                     ordType='Market',
                                                     side='Buy').result()[0]
    market_price = format_price(market_buy_order.get('avgPx'))
    logger.info('Market Buy Avg Price: %.2f' % market_price)

    close_order_price = math.floor(format_price(market_price * 1.004))
    close_order = bitmex_client.Order.Order_new(symbol=SYMBOL,
                                                orderQty=CONTRACTS,
                                                ordType='Limit',
                                                side='Sell',
                                                price=close_order_price).result()[0]

    stop_order_price = math.ceil(format_price(market_price * 0.996))
    logger.info('Stop Order Price: %.2f' % stop_order_price)
    stop_market_order = bitmex_client.Order.Order_new(symbol=SYMBOL,
                                                      orderQty=CONTRACTS,
                                                      ordType='Stop',
                                                      side='Sell',
                                                      stopPx=stop_order_price,
                                                      execInst='LastPrice').result()[0]

    return market_buy_order, stop_market_order, close_order


def poll_orders(close_order: dict) -> None:
    def _poll(order_id):
        logger.info('Polling for order ID: %s' % close_order.get('orderID'))

        order_progress = bitmex_client.Order.Order_getOrders(symbol=SYMBOL,
                                                             filter='{"orderID": "%s"}' % order_id,
                                                             count=1).result()[0][0]
        order_status = order_progress.get('ordStatus')
        if order_status != 'Filled' or order_status != 'Canceled':
            time.sleep(REFRESH_TIME)
            _poll(order_id)

    _poll(close_order.get('orderID'))

    logger.info('Order filled!')
    bitmex_client.Order.Order_cancelAll(symbol=SYMBOL).result()


def main() -> None:
    global LAST_ORDER_FRACTAL

    logger.info('Longing for %d Contracts' % CONTRACTS)
    logger.info('VWMA Period: %d' % VWMA_PERIOD)
    logger.info('Leverage: %d' % LEVERAGE)

    logger.info('Getting klines from Bitmex for TF: %s' % TF)
    candles = get_klines()

    logger.info('Generating fractals..')
    candles = generate_fractals(klines=candles)
    candles = generate_vwma(klines=candles,
                            period=VWMA_PERIOD)

    last_candle = candles[-1]
    candle_with_fractals = list(filter(lambda x: x.get('up_fractal') is not None, candles))
    if len(candle_with_fractals) == 0:
        return
    last_fractal = candle_with_fractals[-1].get('up_fractal')
    logger.info('Last Fractal: %.2f' % last_fractal)

    if last_fractal == LAST_ORDER_FRACTAL:
        logger.info('Bailing, last fractal is still the last order fractal..')
        return

    logger.info('Last Close: %.2f' % last_candle.get('close'))
    logger.info('Last Low: %.2f' % last_candle.get('low'))

    ohc3 = (last_candle.get('open')+last_candle.get('high')+last_candle.get('close'))/3
    green_candle = last_candle.get('close') > last_candle.get('open')

    vwma_value = last_candle.get('vwma')
    logger.info('VWMA: %.2f' % vwma_value)
    vwma_ideal = last_candle.get('low') <= vwma_value

    if vwma_ideal and green_candle and ohc3 > last_fractal:
        orders = create_orders(current_price=last_candle.get('close'))
        logger.info('Market Buy Order ID: %s' % orders[0].get('orderID'))
        logger.info('Close Order ID: %s' % orders[1].get('orderID'))
        logger.info('Stop Market Order ID: %s' % orders[2].get('orderID'))

        message = construct_buy_telegram_message(orders[0], last_fractal, vwma_value)
        send_telegram_message(text=message)

        poll_orders(orders[1])

        message = construct_sell_telegram_message(orders[0], last_fractal, vwma_value)
        send_telegram_message(text=message)

        LAST_ORDER_FRACTAL = last_fractal

        return

    logger.info('No action for now, sleeping..')


def loop():
    while True:
        logger.info('=====================================')
        logger.info('Tick!')
        main()
        logger.info('=====================================\n')
        time.sleep(REFRESH_TIME)


if __name__ == '__main__':
    # Cancel all orders first
    bitmex_client.Order.Order_cancelAll(symbol=SYMBOL).result()

    # When starting first time, let's wait for a while before making orders
    time.sleep(GRACE_PERIOD_IN_MINUTES * 60)
    try:
        loop()
    except HTTPError:
        time.sleep(REFRESH_TIME)
        loop()
