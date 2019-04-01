FROM python:3

COPY . .

RUN pip install -e .[test]

CMD [ "pytest","tests" ]