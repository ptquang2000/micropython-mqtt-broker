FROM python:3

WORKDIR /broker

RUN apt-get update && apt-get install git -y

RUN git clone https://github.com/micropython/micropython /broker/micropython

RUN cd /broker/micropython/mpy-cross && make

RUN cd /broker/micropython/ports/unix && make submodules && make

ENV PYTHONUNBUFFERED=0