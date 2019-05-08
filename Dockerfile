FROM python:3.7

COPY . .

RUN pip install -e .[test]

CMD [ "make", "test" ]
