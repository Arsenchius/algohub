from backtesting import Strategy
import numpy as np


class Simple(Strategy):
    sl_long = 0.99
    tp_long = 1.02
    tp_short = 0.98
    sl_short = 1.01
    size = 0.15

    def init(self):
        self.forecasts = self.I(
            lambda: np.repeat(np.nan, len(self.data)), name="forecast"
        )
        self.open_positions = 0
        self.last_position_size = 0
        self.last_exit_time = self.data.index[0]
        self.last_trade_time = None

        self.close = self.data.Close
        self.high = self.data.High
        self.low = self.data.Low
        self.volume = self.data.Volume

    def next(self):
        close_price = self.data.Close[-1]
        forecast = self.data.Predictions[-1]

        self.forecasts[-1] = forecast
        # print(forecast)
        if forecast == 2 and not self.position.is_long:
            print("bp_2")
            self.position.close()
            self.buy(
                size=self.size,
                sl=close_price * self.sl_long,
                tp=close_price * self.tp_long,
            )
        elif forecast == 0 and not self.position.is_short:
            print("bp_1")
            self.position.close()
            self.sell(
                size=self.size,
                sl=close_price * self.sl_short,
                tp=close_price * self.tp_short,
            )

        for trade in self.trades:
            trade_open_price = trade.entry_price
            if trade.size > 0:
                if (
                    close_price - trade_open_price > 0.004 * trade_open_price
                    and trade.is_long
                ):
                    trade.sl = (1 + 0.0004) / (1 - 0.0004) * trade_open_price
            if trade.size < 0:
                if (
                    trade_open_price - close_price > 0.004 * trade_open_price
                    and trade.is_short
                ):
                    trade.sl = (1 + 0.0004) / (1 - 0.0004) * trade_open_price
