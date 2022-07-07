import logging
import os
import json

from fyers_api.Websocket import ws

from config.Config import getServerConfig
from ticker.BaseTicker import BaseTicker
from instruments.Instruments import Instruments
from models.TickData import TickData
from utils.Utils import Utils

class FyersTicker(BaseTicker):
    def __init__(self):
        super().__init__('fyers')

    def custom_message(self, msg):
        ticks = []
        # print(msg)
        bTick = msg[0]
        tradingSymbol = bTick['symbol']
        tick = TickData(tradingSymbol)
        tick.lastTradedPrice = bTick['ltp']
        tick.lastTradedQuantity = bTick['last_traded_qty']
        tick.avgTradedPrice = bTick['avg_trade_price']
        tick.volume = bTick['vol_traded_today']
        tick.totalBuyQuantity = bTick['tot_buy_qty']
        tick.totalSellQuantity = bTick['tot_sell_qty']
        tick.open = bTick['open_price']
        tick.high = bTick['high_price']
        tick.low = bTick['low_price']
        tick.close = bTick['close_price']
        ticks.append(tick)

        self.onNewTicks(ticks)

    def startTicker(self,symbols):
        if symbols != '':
            brokerAppDetails = self.brokerLogin.getBrokerAppDetails()
            brokerAppDetails.appKey
            accessToken = self.brokerLogin.getAccessToken()
            self.brokerLogin.getAccessToken
            if accessToken == None:
                logging.error('FyersTicker startTicker: Cannot start ticker as accessToken is empty')
                return
            serverConfig = getServerConfig()
            tickerLogs = os.path.join(serverConfig['deployDir'], 'tickerLogs')
            tickerLogs = os.path.join(tickerLogs, Utils.getTodayDateStr())
            wslogsPath = os.path.join(tickerLogs,'tikcer.txt')
            # wslogsPath = os.path.join(path, Utils.getTodayDateStr())
            if os.path.exists(wslogsPath) == False:
                logging.info('TradeManager: Intraday Trades Directory %s does not exist. Hence going to create.', wslogsPath)
                os.makedirs(wslogsPath)
            data_type = 'symbolData'
            print(symbols)
            # symbols = ["NSE:BANKNIFTY2270734200CE", "NSE:BANKNIFTY2270734200PE"]
            wsToken = brokerAppDetails.appKey+':'+accessToken
            ticker = ws.FyersSocket(access_token=str(wsToken),run_background=False,log_path=wslogsPath)
            ticker.websocket_data = self.custom_message
            ticker.subscribe(symbol=symbols,data_type=data_type)
            logging.info('FyersTicker: Going to connect..')
            self.ticker = ticker
            ticker.keep_running()
        
    
    def stopTicker(self):
        self.ticker.stop_running()