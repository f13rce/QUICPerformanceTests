#!/bin/bash

tcpdump -i lo -n udp port 6121 -w packets.pcap
