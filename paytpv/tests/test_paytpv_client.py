# encoding: utf-8
import datetime
import os
import random
import re
from hashlib import sha1

import pytest
from requests.exceptions import ConnectionError

from paytpv.client import PaytpvClient
from paytpv.exc import PaytpvException


T1 = '4539232076648253'
T2 = '5445288852200883'
T3 = '6011454638812167'
T4 = '377960095195350'

NAME = 'Test Vinissimus'
YEAR = datetime.datetime.now().year + 1
CADUCA = '05' + str(YEAR)[2:]  # 05 y año: año actual + 1
CVV = '123'
D3Secure = '1234'


def test_signature(paytpv, settings):

    data = {
        'DS_MERCHANT_MERCHANTCODE': '1',
        'DS_MERCHANT_TERMINAL': '4',
        'DS_MERCHANT_PAN': '2',
        'DS_MERCHANT_EXPIRYDATE': 'no',
        'DS_MERCHANT_CVV2': '3',
        'DS_ORIGINAL_IP': 'no'
        }
    signature = ['DS_MERCHANT_MERCHANTCODE', 'DS_MERCHANT_PAN', 'DS_MERCHANT_CVV2', 'DS_MERCHANT_TERMINAL']

    sign = paytpv.signature(data, signature)
    code = '1234' + settings['MERCHANTPASSWORD']

    assert sign == sha1(code.encode()).hexdigest()


def test_connection(paytpv, settings):
    # ok
    assert paytpv.client

    # connection error
    paytpv = PaytpvClient(settings, ip=None)
    paytpv.PAYTPVWSDL = 'https://localhost'
    with pytest.raises(ConnectionError):
        paytpv.client


def test_add_user(paytpv):
    # error expdate
    with pytest.raises(PaytpvException) as e:
        res = paytpv.add_user(pan='1', expdate='1', cvv='1', name='1')

    assert e.value.code == 109  # Expiry date error

    # new user
    res = paytpv.add_user(pan=T1, expdate=CADUCA, cvv=CVV, name=NAME)
    assert res.DS_ERROR_ID == '0'
    DS_IDUSER = res.DS_IDUSER
    DS_TOKEN_USER = res.DS_TOKEN_USER

    # already added user
    res = paytpv.add_user(pan=T1, expdate=CADUCA, cvv=CVV, name=NAME)
    assert res.DS_ERROR_ID == '0'
    assert DS_IDUSER != res.DS_IDUSER
    assert DS_TOKEN_USER != res.DS_TOKEN_USER
    DS_IDUSER_2 = res.DS_IDUSER
    DS_TOKEN_USER_2 = res.DS_TOKEN_USER

    # remove added users
    res = paytpv.remove_user(idpayuser=DS_IDUSER, tokenpayuser=DS_TOKEN_USER)
    res.DS_RESPONSE == 1
    res.DS_ERROR_ID == 0
    res = paytpv.remove_user(idpayuser=DS_IDUSER_2, tokenpayuser=DS_TOKEN_USER_2)
    res.DS_RESPONSE == 1
    res.DS_ERROR_ID == 0


def test_info_user(paytpv, user):
    id_user = '0'
    token = '0'

    # non-existent user
    with pytest.raises(PaytpvException) as e:
        res = paytpv.info_user(idpayuser=id_user, tokenpayuser=token)

    assert e.value.code == 1001  # User not found. Please contact your administrator

    # Existent user
    DS_IDUSER = user.DS_IDUSER
    DS_TOKEN_USER = user.DS_TOKEN_USER

    res = paytpv.info_user(idpayuser=DS_IDUSER, tokenpayuser=DS_TOKEN_USER)
    assert res.DS_ERROR_ID == 0
    assert res.DS_MERCHANT_PAN == '453923-XX-XXXX-8253'
    assert res.DS_CARD_BRAND == 'VISA'
    assert res.DS_CARD_TYPE == 'CREDIT'
    assert res.DS_CARD_I_COUNTRY_ISO3 == 'ESP'
    assert res.DS_EXPIRYDATE == '{0}/05'.format(YEAR)
    assert res.DS_CARD_HASH == 'd752d8a349d88ba10f5d09f2ec09baba7b527d82d3fdaef175048a15e19e34bc'
    assert res.DS_CARD_CATEGORY == 'BUSINESS'


def test_execute_purchase(paytpv, user):

    # charge non-existent user
    with pytest.raises(PaytpvException) as e:
        res = paytpv.execute_purchase(idpayuser='0', tokenpayuser='0', amount=33, order='3')

    assert e.value.code == 1001  # User not found. Please contact your administrator

    # charge
    DS_IDUSER = user.DS_IDUSER
    DS_TOKEN_USER = user.DS_TOKEN_USER
    DS_MERCHANT_ORDER = str(random.random())

    res = paytpv.execute_purchase(idpayuser=DS_IDUSER, tokenpayuser=DS_TOKEN_USER, amount=33, order=DS_MERCHANT_ORDER)
    assert res.DS_ERROR_ID == 0
    assert res.DS_MERCHANT_AMOUNT == 3300
    assert res.DS_MERCHANT_ORDER == DS_MERCHANT_ORDER
    assert res.DS_MERCHANT_CURRENCY == "EUR"
    assert res.DS_MERCHANT_CARDCOUNTRY == 724


def test_execute_refund(paytpv, user, order):

    # refund
    DS_IDUSER = user.DS_IDUSER
    DS_TOKEN_USER = user.DS_TOKEN_USER
    DS_MERCHANT_ORDER = order.DS_MERCHANT_ORDER
    DS_MERCHANT_AUTHCODE = order.DS_MERCHANT_AUTHCODE

    res = paytpv.execute_refund(
        idpayuser=DS_IDUSER, tokenpayuser=DS_TOKEN_USER, amount=33,
        order=DS_MERCHANT_ORDER, authcode=DS_MERCHANT_AUTHCODE
    )
    assert res.DS_ERROR_ID == 0
    assert res.DS_MERCHANT_ORDER == DS_MERCHANT_ORDER
    assert res.DS_MERCHANT_CURRENCY == "EUR"


def test_get_secure_iframe(paytpv, user, order):
    DS_IDUSER = user.DS_IDUSER
    DS_TOKEN_USER = user.DS_TOKEN_USER
    DS_MERCHANT_ORDER = order.DS_MERCHANT_ORDER
    urlok = "www.vinissimus.com/ok.html"
    urlko = "www.vinissimus.com/ko.html"

    res = paytpv.get_secure_iframe(
        idpayuser=DS_IDUSER, tokenpayuser=DS_TOKEN_USER, amount=33,
        order=DS_MERCHANT_ORDER, language='ES', urlok=urlok, urlko=urlko
    )
    assert isinstance(res, str)
    assert re.match(r"(?:<iframe[^>]*)(?:(?:\/>)|(?:>.*?<\/iframe>))", res) is not None


def test_remove_user(paytpv, user):
    id_user = '0'
    token = '0'

    # remove non-existent user
    with pytest.raises(PaytpvException):
        res = paytpv.remove_user(idpayuser=id_user, tokenpayuser=token)

    # remove added users
    DS_IDUSER = user.DS_IDUSER
    DS_TOKEN_USER = user.DS_TOKEN_USER

    res = paytpv.remove_user(idpayuser=DS_IDUSER, tokenpayuser=DS_TOKEN_USER)
    res.DS_RESPONSE == 1
    res.DS_ERROR_ID == 0
