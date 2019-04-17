# paytpv

## Documentation

Paytpv api SOAP wrap

## Install Requirements

`pip install -e .[test]`

## Run tests

> Need to add paytpv credentials.

`docker run -e MERCHANTCODE=**** -e MERCHANTPASSWORD=**** -e MERCHANTTERMINAL=**** image`

> Or add credentials to the environment and run tests without docker

`make test`

Select tests to run: `make test args="-k test_password"`

## Errors

### DS_ERROR_ID
-----------
>https://docs.paycomet.com/es/documentacion/codigos-de-error?path=es/documentacion/codigos-de-error


### Exceptions
----------

* add_user:
* zeep.exceptions.ValidationError: Missing element DS_MERCHANT_CARDHOLDERNAME (add_user.DS_MERCHANT_CARDHOLDERNAME)

