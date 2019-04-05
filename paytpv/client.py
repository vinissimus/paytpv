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

    def execute_charge(self, idpayuser, tokenpayuser, amount, order,
                       description="", scoring=0, merchant_data="",
                       merchant_description=""):
        """
        * Realiza un cobro mediante llamada soap.
        * @param int $idpayuser Id de usuario en PAYTPV
        * @param string $tokenpayuser Token de usuario en PAYTPV
        * @param decimal $amount Importe del pago 1€ = 100
        * @param string $order Identificador único del pago
        * @return object Objeto de respuesta de la operación
        """
        if amount <= 0:
            raise ValueError(
            u'paytpv.executeCharge(): el importe debe ser positivo: %s' % (
            amount))
        s_amount = str(int(round(amount * 100, 0)))
        if len(order) > 20:
            raise ValueError(
                u'paytpv.executeCharge(): la longitud máxima de order es 20: %s' % (order))
        if len(description) > 40:
            raise ValueError(
                u'paytpv.executeCharge(): la longitud máxima de description es 40: %s' % (description))

        data = {
            'DS_IDUSER': idpayuser,
            'DS_TOKEN_USER': tokenpayuser,
            'DS_MERCHANT_AMOUNT': s_amount,
            'DS_MERCHANT_ORDER': order,
            'DS_MERCHANT_CURRENCY': 'EUR',
            'DS_MERCHANT_PRODUCTDESCRIPTION': description,
            'DS_MERCHANT_OWNER': 'Vinissimus',
            'DS_MERCHANT_SCORING': scoring, 
            'DS_MERCHANT_DATA': merchant_data,
            'DS_MERCHANT_MERCHANTDESCRIPTOR': merchant_description
        }
        signature = 'DS_MERCHANT_MERCHANTCODE + DS_IDUSER + DS_TOKEN_USER + DS_MERCHANT_TERMINAL + DS_MERCHANT_AMOUNT + DS_MERCHANT_ORDER'
        return self.client.service.execute_purchase(**self.data(data, signature))
    
    # def execute_refund(self, idpayuser, tokenpayuser):
    #     """
    #     <message name="execute_refundRequest">
    #         <part name="DS_MERCHANT_MERCHANTCODE" type="xsd:string"/>
    #         <part name="DS_MERCHANT_TERMINAL" type="xsd:string"/>
    #         <part name="DS_IDUSER" type="xsd:string"/>
    #         <part name="DS_TOKEN_USER" type="xsd:string"/>
    #         <part name="DS_MERCHANT_AUTHCODE" type="xsd:string"/>
    #         <part name="DS_MERCHANT_ORDER" type="xsd:string"/>
    #         <part name="DS_MERCHANT_CURRENCY" type="xsd:string"/>
    #         <part name="DS_MERCHANT_MERCHANTSIGNATURE" type="xsd:string"/>
    #         <part name="DS_ORIGINAL_IP" type="xsd:string"/>
    #         <part name="DS_MERCHANT_AMOUNT" type="xsd:string"/>
    #         <part name="DS_MERCHANT_MERCHANTDESCRIPTOR" type="xsd:string"/>
    #     """
    #     data = {
    #         'DS_IDUSER': idpayuser,
    #         'DS_TOKEN_USER': tokenpayuser,
    #         'DS_MERCHANT_AMOUNT': amount,
    #         'DS_MERCHANT_ORDER': order,
    #         'DS_MERCHANT_CURRENCY': 'EUR'
    #     }
    #     signature = 'DS_MERCHANT_MERCHANTCODE + DS_IDUSER + DS_TOKEN_USER + DS_MERCHANT_TERMINAL'
    #     return self.client.service.execute_refund(**self.data(data, signature))