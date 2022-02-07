#!/bin/bash
micropython="$(pwd)/micropython/ports/unix/micropython"
${micropython} -m server.server 127.24.0.4