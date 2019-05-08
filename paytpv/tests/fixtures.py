# encoding: utf-8
import datetime
import random

import os
import pytest

from paytpv.client import PaytpvClient


@pytest.fixture
def settings():
    settings = {
        'MERCHANTCODE': os.environ["MERCHANTCODE"],
        'MERCHANTPASSWORD': os.environ["MERCHANTPASSWORD"],
        'MERCHANTTERMINAL': os.environ["MERCHANTTERMINAL"],
        'PAYTPVURL': "https://secure.paytpv.com/gateway/xml-bankstore",
        'PAYTPVWSDL': "https://secure.paytpv.com/gateway/xml-bankstore?wsdl"
    }
    return settings


@pytest.fixture
def paytpv(settings):
    return PaytpvClient(settings, "1.2.3.4")


@pytest.fixture
def paytpv_async(settings):
    return PaytpvAsyncClient(settings, "1.2.3.4")


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
    res = paytpv.execute_purchase(
        idpayuser=DS_IDUSER, tokenpayuser=DS_TOKEN_USER,
        amount=33, order=DS_MERCHANT_ORDER
    )

    yield res
