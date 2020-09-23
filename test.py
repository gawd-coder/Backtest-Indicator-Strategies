import argparse
import datetime
import backtrader as bt 
import backtrader.indicators as btind
import backtrader.analyzers as btanalyzers
import backtrader.feeds as btfeeds
from Simple import LinComb_Signal, RSI, MACD, Conventional_MA, Crossover_MA, my_EMA, WMA, BB_strat, Counter_bb

import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('Qt5Agg')
plt.switch_backend('Qt5Agg')

# change the "default=XYZ" values if required
parser = argparse.ArgumentParser(description='Backtest the strategy')
parser.add_argument('-C','--CASH',type=float,default=1000.0,help='Total Cash')
parser.add_argument('-S','--STAKE',type=float,default=5,help='Stake')
parser.add_argument('-CM','--COMMISSION',type=float,default=0.001,help='Commission')

args = parser.parse_args()

cerebro = bt.Cerebro()

# Add/Change the strategy
# You may want to change the default cash for different strategy

cerebro.addstrategy(LinComb_Signal)

data = bt.feeds.YahooFinanceData(
        dataname = 'AAPL', 
        fromdate = datetime.datetime(2014, 1, 1),
        todate = datetime.datetime(2018, 1, 31),
        reverse = False
    )

# Add the Data Feed to Cerebro
cerebro.adddata(data)

# Set the specifications
cerebro.broker.setcash(args.CASH)
cerebro.addsizer(bt.sizers.FixedSize, stake=args.STAKE)
cerebro.broker.setcommission(commission=args.COMMISSION)
cerebro.addanalyzer(btanalyzers.SharpeRatio, _name='mysharpe')

# Print out the starting conditions
print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())


thestrats = cerebro.run()
thestrat = thestrats[0]

print('Sharpe Ratio:', thestrat.analyzers.mysharpe.get_analysis())

# Print out the final result
print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

cerebro.plot(iplot = False)
