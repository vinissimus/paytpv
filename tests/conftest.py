# encoding: utf-8
import pytest

from paytpv.client import PaytpvClient
from paytpv.settings import settings


@pytest.fixture
def paytpv():
    paytpv = PaytpvClient(settings, '62.83.129.18')
    yield paytpv
