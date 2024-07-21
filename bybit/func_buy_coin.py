from bybit.models import Trader, Settings, EntryPrice
from pybit.unified_trading import HTTP


def buy_coin_with_stop_loss(symbol, side):
    settings = Settings.objects.last()
    for account in Trader.objects.all():
        session = HTTP(
            api_key=account.api_key,
            api_secret=account.api_secret)

        try:
            # Set leverage
            session.set_leverage(
                category="linear",
                symbol=symbol,
                buyLeverage=str(int(settings.leverage)),
                sellLeverage=str(int(settings.leverage)),
            )
        except Exception:
            pass

        # Get current market price
        market_data = session.get_tickers(category="linear", symbol=symbol)
        market_price = float(market_data['result']['list'][0]['lastPrice'])

        # Calculate quantity to buy based on amount in USD
        qty = settings.amount_usd / market_price
        qty = str(int(qty))

        orders = [{
            'symbol': symbol,
            'side': "Buy",
            'order_type': 'Market',
            'qty': qty,
            'time_in_force': "GTC"
        }]

        order = session.place_batch_order(category='linear', request=orders)
        print(order)

        # Calculate stop loss price
        stop_loss_price = market_price * (1 - settings.stop_loss_percent / 100)

        # Place stop loss order
        session.set_trading_stop(
            category='linear',
            symbol=symbol,
            side="Buy",
            stop_loss=str(stop_loss_price)
        )

        EntryPrice.objects.create(
            symbol=symbol,
            price=market_price
        )


def close_part_position(symbol, target_num):
    for user in Trader.objects.all():
        session = HTTP(
            api_key=user.api_key,
            api_secret=user.api_secret)

        # Get current position
        positions = session.get_positions(category="linear", symbol=symbol)
        print(positions)

        entry_price = EntryPrice.objects.filter(symbol=symbol).last()

        if target_num != 4:
            # stop_loss = price * (1 + target * percent)
            stop_loss = entry_price.price * (1 + (target_num - 1) * Settings.objects.last().stop_loss_step / 100)

            session.set_trading_stop(
                category='linear',
                symbol=symbol,
                side="Buy",
                stop_loss=str(stop_loss)
            )
        else:
            EntryPrice.objects.filter(symbol=symbol).last().delete()

        position_qty = float(positions['result']['list'][0]['size'])

        # Calculate quantity to close (50% of current position)
        close_qty = position_qty / (5 - target_num)
        close_qty = str(round(close_qty, 3))

        orders = [{
            'symbol': symbol,
            'side': "Sell",
            'order_type': 'Market',
            'qty': close_qty,
            'time_in_force': "GTC"
        }]

        session.place_batch_order(category='linear', request=orders)


