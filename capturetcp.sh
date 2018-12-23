#!/bin/bash

tcpdump -i lo -n tcp port 80 -w tcppackets.pcap
