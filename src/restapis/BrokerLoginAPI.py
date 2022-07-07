import logging
from flask.views import MethodView
from flask import request, redirect

from core.Controller import Controller 

class BrokerLoginAPI(MethodView):
  def get(self):
    redirectUrl = Controller.handleBrokerLogin(request.args,request.base_url.split('/')[-1])
    return redirect(redirectUrl, code=302)