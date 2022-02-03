#!/bin/bash
micropython="$(pwd)/micropython/ports/unix/micropython"
echo ${micropython}
${micropython} -m tests.test_connect $(hostname -I)