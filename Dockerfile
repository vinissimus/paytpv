FROM python:3

COPY . .

RUN pip install -e .[test]

CMD [ "make", "test" ]