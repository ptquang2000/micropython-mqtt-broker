#!/bin/bash
micropython="$(pwd)/micropython/ports/unix/micropython"
${micropython} server/broker.py $(hostname -I)