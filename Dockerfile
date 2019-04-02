FROM python:3

RUN apt-get update -y

RUN apt-get install -y  \
       make

COPY . .

RUN pip install -e .[test]

CMD [ "ls", "bin" ]