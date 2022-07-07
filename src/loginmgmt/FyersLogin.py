import os
from config.Config import getSystemConfig, getSystemConfig
import requests
from urllib.parse import urlparse, parse_qs
from fyers_api import accessToken, fyersModel
from flask import redirect
import logging


from loginmgmt.BaseLogin import BaseLogin

class FyersLogin(BaseLogin):
    def __init__(self,brokerAppDetails):
        BaseLogin.__init__(self,brokerAppDetails)
    
    def login(self, args):
        logging.info('==> ZerodhaLogin .args => %s', args)
        systemConfig = getSystemConfig()
        self.brokerAppDetails.redirectUrl
        session = accessToken.SessionModel(client_id=self.brokerAppDetails.appKey, secret_key=self.brokerAppDetails.appSecret, redirect_uri=self.brokerAppDetails.redirectUrl, response_type="code", grant_type="authorization_code")
        redirectUrl = None
        if 'auth_code' in args:
            auth_code = args['auth_code']
            logging.info('Fyers auth_code = %s', auth_code)
            session.set_token(auth_code)
            tokenResponse = session.generate_token()
            token = tokenResponse["access_token"]
            logging.info('Fyers Login successful. accessToken = %s', token)
            brokerhandle = fyersModel.FyersModel(client_id=self.brokerAppDetails.appKey, token=token)

            # set broker handle and access token to the instance
            self.setBrokerHandle(brokerhandle)
            self.setAccessToken(token)

            #refirect to home page with query param loggedIn=true
            homeUrl = systemConfig['homeUrl']+'?loggedIn=true'
            logging.info('Fyers Redirecting to home Page %s',homeUrl)
            redirectUrl = homeUrl
        else:
            loginUrl = 'https://api.fyers.in/api/v2/generate-authcode?client_id='+self.brokerAppDetails.appKey+'&redirect_uri='+self.brokerAppDetails.redirectUrl+'&response_type=code&state=sample_state'
            redirectUrl = loginUrl
        return redirectUrl