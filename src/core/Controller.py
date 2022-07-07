import logging

from config.Config import getBrokerAppConfig
from models.BrokerAppDetails import BrokerAppDetails
from loginmgmt.FyersLogin import FyersLogin
from loginmgmt.ZerodhaLogin import ZerodhaLogin

class Controller:
  brokerLogin = None # static variable
  brokerName = None # static variable

  def handleBrokerLogin(args, brokerName):
    brokerAppConfig = getBrokerAppConfig()
    brokerAppConfig = brokerAppConfig[str(brokerName)]
    brokerAppDetails = BrokerAppDetails(brokerAppConfig['broker'])
    brokerAppDetails.setClientID(brokerAppConfig['clientID'])
    brokerAppDetails.setAppKey(brokerAppConfig['appKey'])
    brokerAppDetails.setAppSecret(brokerAppConfig['appSecret'])
    brokerAppDetails.setRedirectUrl(brokerAppConfig['redirectUrl'])

    logging.info('handleBrokerLogin appKey %s', brokerAppDetails.appKey)
    Controller.brokerName = brokerAppDetails.broker
    if Controller.brokerName == 'zerodha':
      Controller.brokerLogin = ZerodhaLogin(brokerAppDetails)
    if Controller.brokerName == 'fyers':
      Controller.brokerLogin = FyersLogin(brokerAppDetails)

    redirectUrl = Controller.brokerLogin.login(args)
    return redirectUrl

  def getBrokerLogin():
    return Controller.brokerLogin

  def getBrokerName():
    return Controller.brokerName
