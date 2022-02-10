#!/bin/bash
micropython="$(pwd)/micropython/ports/unix/micropython"
${micropython} server/broker.py 127.24.0.4