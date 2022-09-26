#causing slight bt currently, please ignore

import yfinance as yf
import backtrader as bt
import pandas as pd
import datetime
import matplotlib.pyplot as plt
from scipy.stats import linregress
import numpy as np


def calculate_momentum(data):
    log_data = np.log(data)
    x_data = np.arange(len(log_data))
    beta, _, rvalue, _, _ = linregress(x_data, log_data)
    return ((1+beta)**252) * (rvalue**2)


class Momentum(bt.Indicator):
    lines = ('momentum_trend',)
    params = (('period', 90),)

    def __init__(self):
        self.addminperiod(self.params.period)

    def next(self):
        returns = np.log(self.data.get(size=self.params.period))
        x = np.arange(len(returns))
        beta, _, rvalue, _, _ = linregress(x, returns)
        annualized = (1 + beta) ** 252
        self.lines.momentum_trend[0] = annualized * rvalue ** 2


class MomentumStrategy(bt.Strategy):

    def __init__(self):
        self.counter = 0
        self.indicators = {}
        self.sorted_data = []
        self.spy = self.datas[0]
        self.stocks = self.datas[1:]

        for stock in self.stocks:
            self.indicators[stock] = {}
            self.indicators[stock]['momentum'] = Momentum(stock.close, period=90)
            self.indicators[stock]['sma100'] = bt.indicators.\
                SimpleMovingAverage(stock.close, period=100)
            self.indicators[stock]['atr20'] = bt.indicators.ATR(stock, period=20)

        self.sma200 = bt.indicators.MovingAverageSimple(self.spy.close, period=200)

    def prenext(self):
        self.next()

    def next(self):
        if self.counter % 5 == 0:
            self.rebalance_portfolio()
        if self.counter % 10 == 0:
            self.update_positions()

        self.counter += 1

    def rebalance_portfolio(self):

        self.sorted_data = list(filter(lambda stock_data: len(stock_data) > 100, self.stocks))
        self.sorted_data.sort(key=lambda stock: self.indicators[stock]['momentum'][0])
        num_stocks = len(self.sorted_data)

        for index, single_stock in enumerate(self.sorted_data):
            if self.getposition(self.data).size:
                if index > 0.2 * num_stocks or single_stock < self.indicators[single_stock]['sma100']:
                    self.close(single_stock)

        if self.spy < self.sma200:
            return

        for index, single_stock in enumerate(self.sorted_data[:int(0.2 * num_stocks)]):
            cash = self.broker.get_cash()
            value = self.broker.get_value()
            if cash > 0 and not self.getposition(self.data).size:
                size = value * 0.001 / self.indicators[single_stock]["atr20"]
                self.buy(single_stock, size=size)

    def update_positions(self):
        num_stocks = len(self.sorted_data)

        for index, single_stock in enumerate(self.sorted_data[:int(0.2 * num_stocks)]):
            cash = self.broker.get_cash()
            value = self.broker.get_value()
            if cash > 0:
                size = value * 0.001 / self.indicators[single_stock]["atr20"]
                self.order_target_size(single_stock, size)


if __name__ == '__main__':
    stocks = []
    cerebro = bt.Cerebro()

    with open("companies_all") as file_in:
        for line in file_in:
            stocks.append(line.strip('\n'))
            try:
                df = pd.read_csv(line.strip('\n'), parse_dates=True, index_col=0)
                if len(df) > 100:
                    cerebro.adddata(bt.feeds.PandasData(dataname=df, plot=False))
            except FileNotFoundError:
                pass

    cerebro.addobserver(bt.observers.Value)
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, riskfreerate=0.0)
    cerebro.addanalyzer(bt.analyzers.Returns)
    cerebro.addanalyzer(bt.analyzers.DrawDown)
    cerebro.addstrategy(MomentumStrategy)

    cerebro.broker.set_cash(100000)
    # commission fee is 1%
    cerebro.broker.setcommission(0.01)

    print('Initial capital: $%.2f' % cerebro.broker.getvalue())
    results = cerebro.run()

    print(f"Sharpe: {results[0].analyzers.sharperatio.get_analysis()['sharperatio']:.3f}")
    print(f"Norm. Annual Return: {results[0].analyzers.returns.get_analysis()['rnorm100']:.2f}%")
    print(f"Max Drawdown: {results[0].analyzers.drawdown.get_analysis()['max']['drawdown']:.2f}%")
    print('Capital: $%.2f' % cerebro.broker.getvalue())