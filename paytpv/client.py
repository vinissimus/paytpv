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
from hashlib import md5, sha1

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
        * @param int $amount Importe del pago 1€ = 100
        * @param string $order Identificador único del pago
        * @return object Objeto de respuesta de la operación
        """
        if amount <= 0:
            raise ValueError(
                u'paytpv.executeCharge(): el importe debe ser positivo: %s'
                % (amount)
            )
        s_amount = str(int(round(amount * 100, 0)))
        if len(order) > 20:
            raise ValueError(
                u'paytpv.executeCharge(): la longitud máxima de order es 20: %s'
                % (order)
            )
        if len(description) > 40:
            raise ValueError(
                u'paytpv.executeCharge(): la longitud máxima de description es 40: %s'
                % (description)
            )

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
        signature = 'DS_MERCHANT_MERCHANTCODE + DS_IDUSER + DS_TOKEN_USER'
        signature += '+ DS_MERCHANT_TERMINAL + DS_MERCHANT_AMOUNT + DS_MERCHANT_ORDER'
        return self.client.service.execute_purchase(**self.data(data, signature))

    def execute_refund(self, idpayuser, tokenpayuser, amount, order, authcode, merchant_description=""):
        """
        * Realiza devolución mediante llamada soap
        * @param int $idpayuser Id de usuario en PAYTPV
        * @param string $tokenpayuser Token de usuario en PAYTPV
        * @param int $amount Importe del pago 1€ = 100
        * @param string $order Identificador único del pago (debe ser el mismo del cobro)
        * @param string authcode Identificador devuelto en el momento del cobro
        * @return object Objeto de respuesta de la operación
        """
        if amount <= 0:
            raise ValueError(
                u'paytpv.executeCharge(): el importe debe ser positivo: %s'
                % (amount)
            )
        s_amount = str(int(round(amount * 100, 0)))
        if len(order) > 20:
            raise ValueError(
                u'paytpv.executeCharge(): la longitud máxima de order es 20: %s'
                % (order)
            )

        data = {
            'DS_IDUSER': idpayuser,
            'DS_TOKEN_USER': tokenpayuser,
            'DS_MERCHANT_AMOUNT': s_amount,
            'DS_MERCHANT_ORDER': order,
            'DS_MERCHANT_CURRENCY': 'EUR',
            'DS_MERCHANT_AUTHCODE': authcode,
            'DS_MERCHANT_MERCHANTDESCRIPTOR': merchant_description
        }
        signature = 'DS_MERCHANT_MERCHANTCODE + DS_IDUSER + DS_TOKEN_USER '
        signature += '+ DS_MERCHANT_TERMINAL + DS_MERCHANT_AUTHCODE + DS_MERCHANT_ORDER'
        return self.client.service.execute_refund(**self.data(data, signature))

    def get_secure_iframe(self, idpayuser, tokenpayuser, amount, order, language, urlok, urlko):
        """
        * Retorna el codi html del iframe per fer un cobrament securitzat.
        * Operació 109, execute_purchase_token: cobrament a un usuari ja existent.
        """
        if amount <= 0:
            raise ValueError(
                u'paytpv.getSecureIframe(): el importe debe ser positivo: %s' % (amount)
            )
        s_amount = str(int(round(amount * 100, 0)))
        if len(order) > 20:
            raise ValueError(
                u'paytpv.getSecureIframe(): la longitud máxima de order es 20: %s' % (order)
            )

        def iframe_signature(data, signature):
            """
            Cálculo firma:
            md5(MERCHANT_MERCHANTCODE + IDUSER + TOKEN_USER + MERCHANT_TERMINAL
            + OPERATION + MERCHANT_ORDER + MERCHANT_AMOUNT + MERCHANT_CURRENCY + md5(PASSWORD))
            """
            ordered_ds = signature.split('+')
            ordered_ds = map(str.strip, ordered_ds)
            suma = ''.join(map(data.get, ordered_ds))
            suma = suma + md5(self.MERCHANTPASSWORD.encode()).hexdigest()
            return md5(suma.encode()).hexdigest()

        data = {
            'IDUSER': idpayuser,
            'TOKEN_USER': tokenpayuser,
            'OPERATION': "109",
            'MERCHANT_ORDER': order,
            'MERCHANT_AMOUNT': s_amount,
            'MERCHANT_CURRENCY': 'EUR',
            'MERCHANT_MERCHANTCODE': self.MERCHANTCODE,
            'MERCHANT_TERMINAL': self.MERCHANTTERMINAL,
            'ORIGINAL_IP': self.ip
        }
        signature = 'MERCHANT_MERCHANTCODE + IDUSER + TOKEN_USER + MERCHANT_TERMINAL + OPERATION '
        signature += '+ MERCHANT_ORDER + MERCHANT_AMOUNT + MERCHANT_CURRENCY'
        signature = iframe_signature(data, signature)
        params = [
            "MERCHANT_MERCHANTCODE=" + self.MERCHANTCODE,
            "MERCHANT_TERMINAL=" + self.MERCHANTTERMINAL,
            "OPERATION=109",
            "LANGUAGE=" + language,
            "MERCHANT_MERCHANTSIGNATURE=" + signature,
            "MERCHANT_ORDER=" + order,
            "MERCHANT_AMOUNT=" + s_amount,
            "MERCHANT_CURRENCY=EUR",
            "IDUSER=" + idpayuser,
            "TOKEN_USER=" + tokenpayuser,
            "3DSECURE=1",
            "URLOK=" + urlok,
            "URLKO=" + urlko
        ]
        IFRAMEURL = "https://secure.paytpv.com/gateway/bnkgateway.php?%s" % ('&'.join(params))
        return """<iframe id="secure_iframe"
                title="Secure payment"
                allowtransparency="true"
                frameborder="0"
                style="background: #FFFFFF; width:100%%; height:600px"
                src="%s"></iframe>""" % (IFRAMEURL)


#   FUNCIONS EN SQL
#
# def saveCreditCardAlias(zope_context, id_tarjeta, info):
#     """
#         Guarda el alias de la CC a la bbdd.
#     """
#     zope_context.sql.administracion.tarjetas.paytpv.insert.insert_iduser_tarjeta(
#         id_tarjeta=id_tarjeta, iduser=info[1], tokenuser=info[2])


# def saveAuthorization(zope_context, id_tarjeta, importe, info):
#     """
#         Guarda una operació d'autorització per un import donat.
#     """
#     pass


# def deleteCreditCardAlias(zope_context, id_tarjeta):
#     """
#         Esborra el alias de la bbdd.
#     """
#     zope_context.sql.administracion.tarjetas.paytpv.delete.delete_iduser(
#         id_tarjeta=id_tarjeta)


# def getCreditCardAlias(zope_context, id_tarjeta):
#     """
#         Obté el alias d'una tarja
#     """
#     retsql = zope_context.sql.administracion.tarjetas.paytpv.get_info(
#         id_tarjeta=id_tarjeta)
#     if len(retsql) != 0:
#         iduser = retsql[0]['iduser']
#         tokenuser = retsql[0]['tokenuser']
#         return 0, (iduser, tokenuser)
#     else:
#         return 1, None


# def checkCreditCardAlias(zope_context, id_tarjeta):
#     """
#         Comprova que el alias que tenim carregat encara sigui vàlid.
#         Si hi ha algun problema retorna l'error apropiat. Si tot ok, retorna be.
#     """
#     # res a comprovar aquí
#     pass


# def getCreditCardAuthorizedAmount(zope_context, id_tarjeta):
#     """
#         Obté (si hi és), una operació d'autorització prèvia.
#     """
#     return None


# def hasPreAuth():
#     """
#         True si el backend soporta preauth (i està en ús), False en cas contrari
#     """
#     return False
