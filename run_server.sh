#!/bin/bash
micropython="$(pwd)/micropython/ports/unix/micropython"
${micropython} -m server.server $(hostname -I)