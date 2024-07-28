from bybit.models import Trader, Settings, EntryPrice
from pybit.unified_trading import HTTP


def buy_coin_with_stop_loss(symbol, side):
    settings = Settings.objects.last()
    for account in Trader.objects.all():
        session = HTTP(
            api_key=account.api_key,
            api_secret=account.api_secret,
            demo=settings.demo)

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
            'side': side,
            'order_type': 'Market',
            'qty': qty,
            'time_in_force': "GTC"
        }]

        order = session.place_batch_order(category='linear', request=orders)
        print(order)

        # Calculate stop loss price
        if side == "Buy":
            stop_loss_price = market_price * (1 - settings.stop_loss_percent / 100)
        else:
            stop_loss_price = market_price * (1 + settings.stop_loss_percent / 100)

        # Place stop loss order
        session.set_trading_stop(
            category='linear',
            symbol=symbol,
            side=side,
            stop_loss=str(stop_loss_price)
        )

        EntryPrice.objects.create(
            symbol=symbol,
            entry_price=market_price,
            side=side
        )


def close_part_position(symbol, target_num):
    settings = Settings.objects.last()
    for user in Trader.objects.all():
        session = HTTP(
            api_key=user.api_key,
            api_secret=user.api_secret,
            demo=settings.demo)

        positions = session.get_positions(category="linear", symbol=symbol)
        print(positions)

        entry_price = EntryPrice.objects.filter(symbol=symbol).last()

        position_qty = float(positions['result']['list'][0]['size'])

        if target_num == 3:
            close_qty = position_qty
        else:
            close_qty = position_qty / 2

        close_qty = str(round(close_qty, 3))

        if entry_price.side == "Buy":
            close_side = "Sell"
        else:
            close_side = "Buy"

        orders = [{
            'symbol': symbol,
            'side': close_side,
            'order_type': 'Market',
            'qty': close_qty,
            'time_in_force': "GTC"
        }]

        session.place_batch_order(category='linear', request=orders)
        print(target_num)
        print(type(target_num))

        if target_num == 1:
            stop_loss = entry_price.entry_price

            market_data = session.get_tickers(category="linear", symbol=symbol)
            market_price = float(market_data['result']['list'][0]['lastPrice'])

            entry_price.first_target_price = market_price
            entry_price.save()
        elif target_num == 2:
            stop_loss = entry_price.first_target_price
        else:
            EntryPrice.objects.filter(symbol=symbol).last().delete()
            return

        session.set_trading_stop(
            category='linear',
            symbol=symbol,
            side=entry_price.side,
            stop_loss=str(stop_loss)
        )
