import backtrader as bt 
from backtrader.indicators import EMA

class LinComb_Signal(bt.Strategy):
	params=(('long_ravg',25),('short_ravg',12),('max_position',10),('spike_window',4),('cls',0.5),('csr',-0.1),('clr',-0.3))

	def log(self, txt, dt=None):
		''' Logging function for this strategy'''
		dt = dt or self.datas[0].datetime.date(0)
		print('%s, %s' % (dt.isoformat(), txt))

	def __init__(self):
		self.long_RAVG = bt.indicators.SMA(self.data.close,
			period=self.params.long_ravg,plotname='Long Returns Avg')
		self.short_RAVG = bt.indicators.SMA(self.data.close,
			period=self.params.short_ravg,plotname='Short Returns Avg')

		# Long and Short Cross signal
		self.ls_cross=bt.indicators.CrossOver(self.long_RAVG,self.short_RAVG,plotname='LS crossover')
		self.ls_cross_SMA=bt.indicators.SMA(self.ls_cross,
			period=self.params.spike_window,plotname='LS_Spike')

		# Short and Close Cross signal
		self.sr_cross=bt.indicators.CrossOver(self.short_RAVG,self.data.close,plotname='SR crossover')
		self.sr_cross_SMA=bt.indicators.SMA(self.sr_cross,
			period=self.params.spike_window,plotname='SR_Spike')

		# Long and Close Cross signal
		self.lr_cross=bt.indicators.CrossOver(self.long_RAVG,self.data.close,plotname='LR crossover')
		self.lr_cross_SMA=bt.indicators.SMA(self.lr_cross,
			period=self.params.spike_window,plotname='LR_Spike')

	def notify_order(self, order):
		if order.status in [order.Submitted, order.Accepted]:
		# Buy/Sell order submitted/accepted to/by broker - Nothing to do
			return

		# Check if an order has been completed
		# Attention: broker could reject order if not enough cash
		if order.status in [order.Completed]:
			if order.isbuy():
				self.log('BUY EXECUTED, %.2f' % order.executed.price)
			elif order.issell():
				self.log('SELL EXECUTED, %.2f' % order.executed.price)

			self.bar_executed = len(self)

		elif order.status in [order.Canceled, order.Margin, order.Rejected]:
			self.log('Order Canceled/Margin/Rejected')

		# Write down: no pending order
		self.order = None

	def next(self):
		# Create the signal with linear combination of other crossings
		signal = self.params.cls*self.ls_cross + self.params.clr*self.lr_cross+ self.params.csr*self.sr_cross

		# Buy sell Logic
		if signal > 0:
			if self.position.size > 0:
				self.close()
		if signal < 0:
			if self.position.size < self.params.max_position:
				self.buy()
                                            
class RSI(bt.Strategy):
	params=(('min_RSI',35),('max_RSI',65),('max_position',10),('look_back_period',14))

	def log(self, txt, dt=None):
		dt = dt or self.datas[0].datetime.date(0)
		print('%s, %s' % (dt.isoformat(), txt))

	def __init__(self):
		# RSI indicator
		self.RSI = bt.indicators.RSI_SMA(self.data.close, period=self.params.look_back_period) 

	def notify_order(self, order):
		if order.status in [order.Submitted, order.Accepted]:
		# Buy/Sell order submitted/accepted to/by broker - Nothing to do
			return

		# Check if an order has been completed
		# Attention: broker could reject order if not enough cash
		if order.status in [order.Completed]:
			if order.isbuy():
				self.log('BUY EXECUTED, %.2f' % order.executed.price)
			elif order.issell():
				self.log('SELL EXECUTED, %.2f' % order.executed.price)

			self.bar_executed = len(self)

		elif order.status in [order.Canceled, order.Margin, order.Rejected]:
			self.log('Order Canceled/Margin/Rejected')

		# Write down: no pending order
		self.order = None

	def next(self):

		# Buy if over sold
		if self.RSI < self.params.min_RSI:
			self.buy()

		# Sell if over buyed
		if self.RSI > self.params.max_RSI:
			self.close()

class MACD(bt.Strategy):
	params=(('fast_LBP',12),('slow_LBP',26),('max_position',1),('signal_LBP',9))

	def log(self, txt, dt=None):
		''' Logging function for this strategy'''
		dt = dt or self.datas[0].datetime.date(0)
		print('%s, %s' % (dt.isoformat(), txt))

	def __init__(self):
		self.fast_EMA = EMA(self.data, period=self.params.fast_LBP)
		self.slow_EMA = EMA(self.data, period=self.params.slow_LBP)

		self.MACD=self.fast_EMA-self.slow_EMA
		self.Signal = EMA(self.MACD, period=self.params.signal_LBP)
		self.Crossing = bt.indicators.CrossOver(self.MACD,self.Signal,plotname='Buy_Sell_Line')
		self.Hist = self.MACD - self.Signal
		
	def notify_order(self, order):
		if order.status in [order.Submitted, order.Accepted]:
		# Buy/Sell order submitted/accepted to/by broker - Nothing to do
			return

		# Check if an order has been completed
		# Attention: broker could reject order if not enough cash
		if order.status in [order.Completed]:
			if order.isbuy():
				self.log('BUY EXECUTED, %.2f' % order.executed.price)
			elif order.issell():
				self.log('SELL EXECUTED, %.2f' % order.executed.price)

			self.bar_executed = len(self)

		elif order.status in [order.Canceled, order.Margin, order.Rejected]:
			self.log('Order Canceled/Margin/Rejected')

		# Write down: no pending order
		self.order = None

	def next(self):

		# If MACD is above Signal line
		if self.Crossing > 0:
			if self.position.size < self.params.max_position:
				self.buy()

		# If MACD is below Signal line
		elif self.Crossing < 0:
			if self.position.size > 0:
				self.close()

class Conventional_MA(bt.Strategy):
    params = (
        ('maperiod', 25),
    )

    def log(self, txt, dt = None):
        '''Printing function for the complete strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s %s' % (dt.isoformat(), txt))
    
    def __init__(self):
        self.dataclose = self.datas[0].close

        # To keep track of pending orders and buy price/commission
        self.order = None
        self.buyprice = None
        self.buycomm = None

        #Adding SMA indicator
        self.sma = bt.indicators.SimpleMovingAverage(
            self.datas[0], period = self.params.maperiod
        )

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
        
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm)
                )

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            
            else:
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm: %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))
                
                self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')
        
        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return 

        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' % (trade.pnl, trade.pnlcomm))

    def next(self):
        self.log('Close, %.2f' % self.dataclose[0])

        if self.order:
            return

        #check if we are in market
        if not self.position:
            if self.dataclose[0] > self.sma[0]:
                self.log('BUY CREATE, %.2f' % self.dataclose[0])
                self.order = self.buy()
        else:
            if self.dataclose[0] < self.sma[0]:
                self.log('SELL CREATE, %.2f' % self.dataclose[0])
                self.order = self.sell()

class Crossover_MA(bt.Strategy):
    params = (
        ('smallmaperiod', 25),
        ('longmaperiod', 100)
    )

    def log(self, txt, dt = None):
        '''Printing function for the complete strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s %s' % (dt.isoformat(), txt))
    
    def __init__(self):
        self.dataclose = self.datas[0].close

        # To keep track of pending orders and buy price/commission
        self.order = None
        self.buyprice = None
        self.buycomm = None

        #Adding SMA indicator
        self.smallsma = bt.indicators.SimpleMovingAverage(
            self.datas[0], period = self.params.smallmaperiod
        )
        self.longsma = bt.indicators.SimpleMovingAverage(
            self.datas[0], period = self.params.longmaperiod
        )

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
        
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm)
                )

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            
            else:
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm: %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))
                
                self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')
        
        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return 

        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' % (trade.pnl, trade.pnlcomm))

    def next(self):
        self.log('Close, %.2f' % self.dataclose[0])

        if self.order:
            return

        #check if we are in market
        if not self.position:
            if self.smallsma[0] > self.longsma[0]:
                self.log('BUY CREATE, %.2f' % self.dataclose[0])
                self.order = self.buy()
        else:
            if self.smallsma[0] < self.longsma[0]:
                self.log('SELL CREATE, %.2f' % self.dataclose[0])
                self.order = self.sell()

class my_EMA(bt.Strategy):
    params = (
        ('maperiod', 35),
    )

    def log(self, txt, dt = None):
        '''Printing function for the complete strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s %s' % (dt.isoformat(), txt))
    
    def __init__(self):
        self.dataclose = self.datas[0].close

        # To keep track of pending orders and buy price/commission
        self.order = None
        self.buyprice = None
        self.buycomm = None

        #Adding SMA indicator
        self.sma = bt.indicators.ExponentialMovingAverage(
            self.datas[0], period = self.params.maperiod
        )

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
        
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm)
                )

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            
            else:
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm: %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))
                
                self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')
        
        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return 

        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' % (trade.pnl, trade.pnlcomm))

    def next(self):
        self.log('Close, %.2f' % self.dataclose[0])

        if self.order:
            return

        #check if we are in market
        if not self.position:
            if self.dataclose[0] > self.sma[0]:
                self.log('BUY CREATE, %.2f' % self.dataclose[0])
                self.order = self.buy()
        else:
            if self.dataclose[0] < self.sma[0]:
                self.log('SELL CREATE, %.2f' % self.dataclose[0])
                self.order = self.sell()

class WMA(bt.Strategy):
    params = (
        ('maperiod', 30),
    )

    def log(self, txt, dt = None):
        '''Printing function for the complete strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s %s' % (dt.isoformat(), txt))
    
    def __init__(self):
        self.dataclose = self.datas[0].close

        # To keep track of pending orders and buy price/commission
        self.order = None
        self.buyprice = None
        self.buycomm = None

        #Adding SMA indicator
        self.sma = bt.indicators.WeightedMovingAverage(
            self.datas[0], period = self.params.maperiod
        )

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
        
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm)
                )

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            
            else:
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm: %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))
                
                self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')
        
        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return 

        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' % (trade.pnl, trade.pnlcomm))

    def next(self):
        self.log('Close, %.2f' % self.dataclose[0])

        if self.order:
            return

        #check if we are in market
        if not self.position:
            if self.dataclose[0] > self.sma[0]:
                self.log('BUY CREATE, %.2f' % self.dataclose[0])
                self.order = self.buy()
        else:
            if self.dataclose[0] < self.sma[0]:
                self.log('SELL CREATE, %.2f' % self.dataclose[0])
                self.order = self.sell()
    
class BB_strat(bt.Strategy):
    params = (
        ('maperiod', 30 ),
    )

    def log(self, txt, dt = None):
        '''Printing function for the complete strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s %s' % (dt.isoformat(), txt))
    
    def __init__(self):
        self.dataclose = self.datas[0].close

        # To keep track of pending orders and buy price/commission
        self.order = None
        self.buyprice = None
        self.buycomm = None

        #Adding SMA indicator
        self.bbands = bbands = bt.indicators.BBands(self.datas[0])

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
        
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm)
                )

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            
            else:
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm: %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))
                
                self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')
        
        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return 

        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' % (trade.pnl, trade.pnlcomm))

    def next(self):
        self.log('Close, %.2f' % self.dataclose[0])

        if self.order:
            return

        #check if we are in market
        if not self.position:
            if self.bbands[0] < self.dataclose[0]:
                self.log('BUY CREATE, %.2f' % self.dataclose[0])
                self.order = self.buy()
        else:
            if self.bbands[0] > self.dataclose[0]:
                self.log('SELL CREATE, %.2f' % self.dataclose[0])
                self.order = self.sell()
   
class Counter_bb(bt.Strategy):
    params = (
        ('maperiod', 30 ),
    )

    def log(self, txt, dt = None):
        '''Printing function for the complete strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s %s' % (dt.isoformat(), txt))
    
    def __init__(self):
        self.dataclose = self.datas[0].close

        # To keep track of pending orders and buy price/commission
        self.order = None
        self.buyprice = None
        self.buycomm = None

        #Adding SMA indicator
        self.bbands = bbands = bt.indicators.BBands(self.datas[0])

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
        
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm)
                )

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            
            else:
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm: %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))
                
                self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')
        
        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return 

        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' % (trade.pnl, trade.pnlcomm))

    def next(self):
        self.log('Close, %.2f' % self.dataclose[0])

        if self.order:
            return

        #check if we are in market
        if not self.position:
            if self.bbands[0] > self.dataclose[0]:
                self.log('BUY CREATE, %.2f' % self.dataclose[0])
                self.order = self.buy()
        else:
            if self.bbands[0] < self.dataclose[0]:
                self.log('SELL CREATE, %.2f' % self.dataclose[0])
                self.order = self.sell()

