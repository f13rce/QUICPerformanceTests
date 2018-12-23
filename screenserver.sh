#!/bin/bash

# Kill existing server [if it exists]
screen -X -r quic.server kill

# Spawn new one and detach from it
screen -S quic.server -d -m ./startserver.sh
#screen -S quic.server -m ./startserver.sh
