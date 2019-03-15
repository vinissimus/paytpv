# encoding: utf-8
"""

DS_ERROR_ID
-----------
https://docs.paycomet.com/es/documentacion/codigos-de-error?path=es/documentacion/codigos-de-error


Excepcions
----------

add_user
zeep.exceptions.ValidationError: Missing element DS_MERCHANT_CARDHOLDERNAME (add_user.DS_MERCHANT_CARDHOLDERNAME)


"""
from hashlib import sha1

from zeep import Client


class PaytpvClient():

    def __init__(self, settings, ip):
        """
        :param ip: Dirección IP del cliente
        """
        self.ip = ip
        self.MERCHANTCODE = settings.MERCHANTCODE
        self.MERCHANTPASSWORD = settings.MERCHANTPASSWORD
        self.MERCHANTTERMINAL = settings.MERCHANTTERMINAL
        self.PAYTPVURL = settings.PAYTPVURL
        self.PAYTPVWSDL = settings.PAYTPVWSDL

    @property
    def client(self):
        return Client(self.PAYTPVWSDL)

    def signature(self, data, suma_ds):
        """
        """
        ordered_ds = suma_ds.split('+')
        ordered_ds = map(str.strip, ordered_ds)
        suma = ''.join(map(data.get, ordered_ds))
        suma = suma + self.MERCHANTPASSWORD
        return sha1(suma.encode()).hexdigest()

    def data(self, data, signature):
        """Base SOAP request data with signature"""
        base_data = {
            'DS_MERCHANT_MERCHANTCODE': self.MERCHANTCODE,  # Código de cliente
            'DS_MERCHANT_TERMINAL': self.MERCHANTTERMINAL,  # Número de terminal
            'DS_ORIGINAL_IP': self.ip,  # Dirección IP del cliente
            }
        data.update(base_data)
        data['DS_MERCHANT_MERCHANTSIGNATURE'] = self.signature(data, signature)
        return data

    def add_user(self, pan, expdate, cvv, name):
        """
        * Añade una tarjeta a PAYTPV. ¡¡¡ IMPORTANTE !!! Esta entrada directa debe ser activada por PAYTPV.
        * En su defecto el método de entrada de tarjeta para el cumplimiento del
          PCI-DSS debe ser AddUserUrl o AddUserToken (método utilizado por BankStore JET)
        * @param int $pan Número de tarjeta, sin espacios ni guiones
        * @param string $expdate Fecha de caducidad de la tarjeta,
          expresada como “mmyy” (mes en dos cifras y año en dos cifras)
        * @param string $cvv Código CVC2 de la tarjeta
        * @return object Objeto de respuesta de la operación

        :return:
         {
          'DS_IDUSER': '0',
          'DS_TOKEN_USER': '0',
          'DS_ERROR_ID': '0'  # 0 no error, else error code
          }
        """
        data = {
            'DS_MERCHANT_PAN': pan,  # Número de tarjeta, sin espacios ni guiones {16,19}
            'DS_MERCHANT_EXPIRYDATE': expdate,  # Fecha de caducidad mmyy
            'DS_MERCHANT_CVV2': cvv,  # Código CVC2 {3,4}
            'DS_MERCHANT_CARDHOLDERNAME': name
            }
        signature = 'DS_MERCHANT_MERCHANTCODE + DS_MERCHANT_PAN + DS_MERCHANT_CVV2 + DS_MERCHANT_TERMINAL'
        return self.client.service.add_user(**self.data(data, signature))

    def info_user(self, idpayuser, tokenpayuser):
        """
        * Devuelve la información de un usuario almacenada en PAYTPV mediante llamada soap
        * @param int $idpayuser Id del usuario en PAYTPV
        * @param string $tokenpayuser Token del usuario en PAYTPV
        * @return object Objeto de respuesta de la operación
        """
        data = {
            'DS_IDUSER': idpayuser,
            'DS_TOKEN_USER': tokenpayuser
            }
        signature = 'DS_MERCHANT_MERCHANTCODE + DS_IDUSER + DS_TOKEN_USER + DS_MERCHANT_TERMINAL'
        return self.client.service.info_user(**self.data(data, signature))

    def remove_user(self, idpayuser, tokenpayuser):
        """
        * Elimina un usuario de PAYTPV mediante llamada soap
        * @param int $idpayuser Id de usuario en PAYTPV
        * @param string $tokenpayuser Token de usuario en PAYTPV
        * @return object Objeto de respuesta de la operación

        :return: DS_RESPONSE: 0 error, 1 completat

        """
        data = {
            'DS_IDUSER': idpayuser,
            'DS_TOKEN_USER': tokenpayuser
            }
        signature = 'DS_MERCHANT_MERCHANTCODE + DS_IDUSER + DS_TOKEN_USER + DS_MERCHANT_TERMINAL'
        return self.client.service.remove_user(**self.data(data, signature))
