# encoding: utf-8
import datetime
import os
import random
import re
from hashlib import sha1

import pytest
from requests.exceptions import ConnectionError

from paytpv.client import PaytpvClient
from paytpv.settings import settings


T1 = '4539232076648253'
T2 = '5445288852200883'
T3 = '6011454638812167'
T4 = '377960095195350'

NAME = 'Test Vinissimus'
YEAR = datetime.datetime.now().year + 1
CADUCA = '05' + str(YEAR)[2:]  # 05 y año: año actual + 1
CVV = '123'
D3Secure = '1234'


def test_signature():

    data = {
        'DS_MERCHANT_MERCHANTCODE': '1',
        'DS_MERCHANT_TERMINAL': '4',
        'DS_MERCHANT_PAN': '2',
        'DS_MERCHANT_EXPIRYDATE': 'no',
        'DS_MERCHANT_CVV2': '3',
        'DS_ORIGINAL_IP': 'no'
        }
    signature = 'DS_MERCHANT_MERCHANTCODE + DS_MERCHANT_PAN + DS_MERCHANT_CVV2 + DS_MERCHANT_TERMINAL'

    paytpv = PaytpvClient(settings, ip=None)
    sign = paytpv.signature(data, signature)
    code = '1234' + settings.MERCHANTPASSWORD

    assert sign == sha1(code.encode()).hexdigest()


def test_connection():
    # ok
    paytpv = PaytpvClient(settings, ip=None)
    assert paytpv.client

    # connection error
    paytpv.PAYTPVWSDL = 'https://localhost'
    with pytest.raises(ConnectionError):
        paytpv.client


def test_add_user():
    paytpv = PaytpvClient(settings, ip='1')

    # error expdate
    res = paytpv.add_user(pan='1', expdate='1', cvv='1', name='1')
    assert res.DS_ERROR_ID == '109'  # Error en FechaCaducidad
    assert res.DS_IDUSER == '0'
    assert res.DS_TOKEN_USER == '0'

    # new user
    res = paytpv.add_user(pan=T1, expdate=CADUCA, cvv=CVV, name=NAME)
    assert res.DS_ERROR_ID == '0'
    DS_IDUSER = res.DS_IDUSER
    DS_TOKEN_USER = res.DS_TOKEN_USER
    os.environ['DS_IDUSER'] = DS_IDUSER
    os.environ['DS_TOKEN_USER'] = DS_TOKEN_USER

    # already added user
    res = paytpv.add_user(pan=T1, expdate=CADUCA, cvv=CVV, name=NAME)
    assert res.DS_ERROR_ID == '0'
    assert DS_IDUSER != res.DS_IDUSER
    assert DS_TOKEN_USER != res.DS_TOKEN_USER
    os.environ['DS_IDUSER_2'] = res.DS_IDUSER
    os.environ['DS_TOKEN_USER_2'] = res.DS_TOKEN_USER


def test_info_user():
    id_user = '0'
    token = '0'
    ip = '1'
    paytpv = PaytpvClient(settings, ip)

    # non-existent user
    res = paytpv.info_user(idpayuser=id_user, tokenpayuser=token)
    assert res.DS_ERROR_ID == 1001  # Usuario no encontrado.

    # Existent user
    DS_IDUSER = os.environ['DS_IDUSER']
    DS_TOKEN_USER = os.environ['DS_TOKEN_USER']

    res = paytpv.info_user(idpayuser=DS_IDUSER, tokenpayuser=DS_TOKEN_USER)
    assert res.DS_ERROR_ID == 0
    assert res.DS_MERCHANT_PAN == '453923-XX-XXXX-8253'
    assert res.DS_CARD_BRAND == 'VISA'
    assert res.DS_CARD_TYPE == 'CREDIT'
    assert res.DS_CARD_I_COUNTRY_ISO3 == 'ESP'
    assert res.DS_EXPIRYDATE == '{0}/05'.format(YEAR)
    assert res.DS_CARD_HASH == 'd752d8a349d88ba10f5d09f2ec09baba7b527d82d3fdaef175048a15e19e34bc'
    assert res.DS_CARD_CATEGORY == 'BUSINESS'


def test_execute_charge():
    paytpv = PaytpvClient(settings, ip='62.83.129.18')

    # charge non-existent user
    res = paytpv.execute_charge(idpayuser='0', tokenpayuser='0', amount=33, order='3')
    assert res.DS_ERROR_ID == 1001

    # charge
    DS_IDUSER = os.environ['DS_IDUSER']
    DS_TOKEN_USER = os.environ['DS_TOKEN_USER']
    DS_MERCHANT_ORDER = str(random.random())
    os.environ['DS_MERCHANT_ORDER'] = DS_MERCHANT_ORDER

    res = paytpv.execute_charge(idpayuser=DS_IDUSER, tokenpayuser=DS_TOKEN_USER, amount=33, order=DS_MERCHANT_ORDER)
    assert res.DS_ERROR_ID == 0
    assert res.DS_MERCHANT_AMOUNT == 3300
    assert res.DS_MERCHANT_ORDER == DS_MERCHANT_ORDER
    assert res.DS_MERCHANT_CURRENCY == "EUR"
    assert res.DS_MERCHANT_CARDCOUNTRY == 724
    os.environ['DS_MERCHANT_AUTHCODE'] = res.DS_MERCHANT_AUTHCODE


def test_execute_refund():
    paytpv = PaytpvClient(settings, ip='62.83.129.18')

    # refund
    DS_IDUSER = os.environ['DS_IDUSER']
    DS_TOKEN_USER = os.environ['DS_TOKEN_USER']
    DS_MERCHANT_ORDER = os.environ['DS_MERCHANT_ORDER']
    DS_MERCHANT_AUTHCODE = os.environ['DS_MERCHANT_AUTHCODE']

    res = paytpv.execute_refund(
        idpayuser=DS_IDUSER, tokenpayuser=DS_TOKEN_USER, amount=33,
        order=DS_MERCHANT_ORDER, authcode=DS_MERCHANT_AUTHCODE
    )
    assert res.DS_ERROR_ID == 0
    assert res.DS_MERCHANT_ORDER == DS_MERCHANT_ORDER
    assert res.DS_MERCHANT_CURRENCY == "EUR"


def test_get_secure_iframe():
    paytpv = PaytpvClient(settings, ip='62.83.129.18')
    DS_IDUSER = os.environ['DS_IDUSER']
    DS_TOKEN_USER = os.environ['DS_TOKEN_USER']
    DS_MERCHANT_ORDER = os.environ['DS_MERCHANT_ORDER']
    urlok = "www.vinissimus.com/ok.html"
    urlko = "www.vinissimus.com/ko.html"

    res = paytpv.get_secure_iframe(
        idpayuser=DS_IDUSER, tokenpayuser=DS_TOKEN_USER, amount=33,
        order=DS_MERCHANT_ORDER, language='ES', urlok=urlok, urlko=urlko
    )
    assert isinstance(res, str)
    assert re.match(r"(?:<iframe[^>]*)(?:(?:\/>)|(?:>.*?<\/iframe>))", res) is not None


def test_remove_user():
    id_user = '0'
    token = '0'
    ip = '1'
    paytpv = PaytpvClient(settings, ip)

    # remove non-existent user
    res = paytpv.remove_user(idpayuser=id_user, tokenpayuser=token)
    assert res.DS_ERROR_ID == 1001  # Usuario no encontrado.

    # remove added users
    DS_IDUSER = os.environ['DS_IDUSER']
    DS_TOKEN_USER = os.environ['DS_TOKEN_USER']
    DS_IDUSER_2 = os.environ['DS_IDUSER_2']
    DS_TOKEN_USER_2 = os.environ['DS_TOKEN_USER_2']

    res = paytpv.remove_user(idpayuser=DS_IDUSER, tokenpayuser=DS_TOKEN_USER)
    res.DS_RESPONSE == 1
    res.DS_ERROR_ID == 0
    res = paytpv.remove_user(idpayuser=DS_IDUSER_2, tokenpayuser=DS_TOKEN_USER_2)
    res.DS_RESPONSE == 1
    res.DS_ERROR_ID == 0
