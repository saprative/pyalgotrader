import json
import logging

from ordermgmt.BaseOrderManager import BaseOrderManager
from ordermgmt.Order import Order

from models.ProductType import ProductType
from models.OrderType import OrderType
from models.Direction import Direction
from models.OrderStatus import OrderStatus

from utils.Utils import Utils

class FyersOrderManager(BaseOrderManager):
    
    def __init__(self):
        super().__init__('Fyers')

    def placeOrder(self, orderInputParams):
        logging.info('%s: Going to place order with params %s', self.broker, orderInputParams)
        fyers = self.brokerHandle
        try:
            data = {
                "symbol": orderInputParams.tradingSymbol,
                "qty": orderInputParams.qty,
                "type": self.convertToBrokerOrderType(orderInputParams.orderType), 
                "side": self.convertToBrokerDirection(orderInputParams.direction),
                "productType": self.convertToBrokerProductType(orderInputParams.productType),
                "limitPrice": 0 if orderInputParams.orderType=='MARKET' else float(orderInputParams.price),
                "stopPrice": 0,
                "validity": "DAY",
                "disclosedQty": 0,
                "offlineOrder": "False",
                "stopLoss": 0,
                "takeProfit": 0
            }
            orderId = fyers.place_order(data)
            print(data)
            print(orderInputParams.price)
            print(json.dumps(orderId))
            orderId = orderId['id']
            order = Order(orderInputParams)
            order.orderId = orderId
            order.orderPlaceTimestamp = Utils.getEpoch()
            order.lastOrderUpdateTimestamp = Utils.getEpoch()
            print(orderId)
            return order
        except Exception as e:
            logging.info('%s Order placement failed: %s', self.broker, str(e))
            raise Exception(str(e))

    def modifyOrder(self, order, orderModifyParams):
        logging.info('%s: Going to modify order with params %s', self.broker, orderModifyParams)
        fyers = self.brokerHandle
        try:
            data = {
                "id": order.orderId, 
                "type": orderModifyParams.newOrderType if orderModifyParams.newOrderType != None else None, 
                "limitPrice": orderModifyParams.newTriggerPrice if orderModifyParams.newTriggerPrice > 0 else None,
                "qty": orderModifyParams.newQty if orderModifyParams.newQty > 0 else None
            }
            fyers.modify_order(data)

            logging.info('%s Order modified successfully for orderId = %s', self.broker, order.orderId)
            order.lastOrderUpdateTimestamp = Utils.getEpoch()
            return order
        except Exception as e:
            logging.info('%s Order modify failed: %s', self.broker, str(e))
            raise Exception(str(e))
    
    def modifyOrderToMarket(self, order):
        logging.info('%s: Going to modify order with params %s', self.broker)
        fyers = self.brokerHandle
        try:
            data = {
                "id": order.orderId, 
                "type": 2
            }
            fyers.modify_order(data)

            logging.info('%s Order modified successfully to MARKET for orderId = %s', self.broker, order.orderId)
            order.lastOrderUpdateTimestamp = Utils.getEpoch()
            return order
        except Exception as e:
            logging.info('%s Order modify to market failed: %s', self.broker, str(e))
            raise Exception(str(e))

    def cancelOrder(self, order):
        logging.info('%s Going to cancel order %s', self.broker, order.orderId)
        fyers = self.brokerHandle
        try:
            data = {"id":order.orderId}
            orderId = fyers.cancel_order(data)
            logging.info('%s Order cancelled successfully, orderId = %s', self.broker, order.orderId)
            order.lastOrderUpdateTimestamp = Utils.getEpoch()
            return order
        except Exception as e:
            logging.info('%s Order cancel failed: %s', self.broker, str(e))
            raise Exception(str(e))

    def fetchAndUpdateAllOrderDetails(self, orders):
        logging.info('%s Going to fetch order book', self.broker)
        fyers = self.brokerHandle
        orderBook = None
        try:
            orderBook = fyers.orderbook()
        except Exception as e:
            logging.error('%s Failed to fetch order book', self.broker)
            return
        orderBook = orderBook['orderBook']
        print(orderBook)
        logging.info('%s Order book length = %d', self.broker, len(orderBook))
        numOrdersUpdated = 0
        foundOrder = None
        for bOrder in orderBook:
            print(bOrder)
            for order in orders:
                if order.orderId == bOrder[0]['id']:
                    foundOrder = order
                    break
        
        if foundOrder != None:
            logging.info('Found order for orderId %s', foundOrder.orderId)
            foundOrder.qty = bOrder['quantity']
            foundOrder.filledQty = bOrder['filled_quantity']
            foundOrder.pendingQty = bOrder['pending_quantity']
            foundOrder.orderStatus = bOrder['status']
            if foundOrder.orderStatus == OrderStatus.CANCELLED and foundOrder.filledQty > 0:
                # Consider this case as completed in our system as we cancel the order with pending qty when strategy stop timestamp reaches
                foundOrder.orderStatus = OrderStatus.COMPLETED
            foundOrder.price = bOrder['price']
            foundOrder.triggerPrice = bOrder['trigger_price']
            foundOrder.averagePrice = bOrder['average_price']
            logging.info('%s Updated order %s', self.broker, foundOrder)
            numOrdersUpdated += 1

        logging.info('%s: %d orders updated with broker order details', self.broker, numOrdersUpdated)

    def convertToBrokerProductType(self, productType):
        fyers = self.brokerHandle
        if productType == ProductType.MIS:
            return "INTRADAY"
        elif productType == ProductType.NRML:
            return "CNC"
        elif productType == ProductType.CNC:
            return "CNC"
        return None 

    def convertToBrokerOrderType(self, orderType):
        fyers = self.brokerHandle
        if orderType == OrderType.LIMIT:
            return 1
        elif orderType == OrderType.MARKET:
            return 2
        elif orderType == OrderType.SL_MARKET:
            return 3
        elif orderType == OrderType.SL_LIMIT:
            return 4
        return None

    def convertToBrokerDirection(self, direction):
        fyers = self.brokerHandle
        if direction == Direction.LONG:
            return 1
        elif direction == Direction.SHORT:
            return -1
        return None
