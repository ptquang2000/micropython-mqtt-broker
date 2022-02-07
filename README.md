# MQTT BROKER IMPLEMENTATION WITH MICROPYTHON

## Main Goal
- Be able to work with paho-mqtt. 
- Be able to run on ESP ? :D ?

## About
* MQTT version 3.1.1
* Tested features in [tests directory](tests)

## Test MQTT Broker
```bash
# clone repository
git clone --recursive https://github.com/ptquang2000/micropython-mqtt-broker ./mqttbroker
# build micropython
sudo apt-get install build-essential libffi-dev git pkg-config
cd mqttbroker/micropython/ports/unix
make submodules
make
# start server
cd ../../..
chmod +x ./start_server.sh
./start_server.sh 
```