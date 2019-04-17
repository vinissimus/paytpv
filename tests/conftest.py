# encoding: utf-8
import datetime
import os
import random

import pytest
from zeep import Client

from paytpv.client import PaytpvClient


settings = {
    'MERCHANTCODE': os.environ['MERCHANTCODE'],
    'MERCHANTPASSWORD': os.environ['MERCHANTPASSWORD'],
    'MERCHANTTERMINAL': os.environ['MERCHANTTERMINAL'],
    'PAYTPVURL': "https://secure.paytpv.com/gateway/xml-bankstore",
    'PAYTPVWSDL': "https://secure.paytpv.com/gateway/xml-bankstore?wsdl"
}


@pytest.fixture
def paytpv():
    paytpv = PaytpvClient(settings, '62.83.129.18', Client(settings['PAYTPVWSDL']))
    yield paytpv


@pytest.fixture
def user(paytpv):
    NAME = 'Test Vinissimus'
    YEAR = datetime.datetime.now().year + 1
    CADUCA = '05' + str(YEAR)[2:]
    CVV = '123'
    T1 = '4539232076648253'

    res = paytpv.add_user(pan=T1, expdate=CADUCA, cvv=CVV, name=NAME)

    yield res


@pytest.fixture
def order(paytpv, user):
    DS_IDUSER = user.DS_IDUSER
    DS_TOKEN_USER = user.DS_TOKEN_USER
    DS_MERCHANT_ORDER = str(random.random())
    res = paytpv.execute_charge(
        idpayuser=DS_IDUSER, tokenpayuser=DS_TOKEN_USER,
        amount=33, order=DS_MERCHANT_ORDER
    )

    yield res
