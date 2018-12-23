import argparse
import os
import sys

# Commands used from https://calomel.org/network_loss_emulation.html

# Main
parser = argparse.ArgumentParser()

# python3 test_smb.py -d /sne/home/USER/smb-nfs-performance/10kbfiles -s IPADDRESS -u USER -p PASSWORD -o 10kbfilestest -n 10kbtest
parser.add_argument("-i", "--interface", help="Interface of the network to simulate on (e.g.: eth0, eno1, wlan0, etc..)", required=True)
parser.add_argument("-l", "--loss", help="Ratio of the packet loss (e.g.: 0.5 for 50% loss)", required=True)
parser.add_argument("-p", "--ping", help="Additional latency on top of the current latency (e.g.: 100 for 100ms)", required=True)
parser.add_argument("-s", "--spike", help="Random latency spikes on top of the additional latency (e.g.: 50 for 50ms)", required=True)
parser.add_argument("-d", "--duplication", help="Ratio of the packet duplication (e.g.: 0.15 for 15% duplication)", required=True)
parser.add_argument("-r", "--reordering", help="Ratio of the packet reordering (e.g.: 0.05 for 5% reordering)", required=True)

args = parser.parse_args()

# Verify arguments
# Packet loss
args.loss = float(args.loss) # Convert to float
if (args.loss < 0.0 or args.loss > 1.0):
	print("Invalid argument for 'loss': Needs to be in the range of 0.0 and 1.0. You said: " + args.loss)
	sys.exit()
args.loss = round(args.loss*100, 1)

# Packet duping
args.duplication = float(args.duplication) # Convert to float
if (args.duplication < 0.0 or args.duplication > 1.0):
	print("Invalid argument for 'duplication': Needs to be in the range of 0.0 and 1.0. You said: " + args.duplication)
	sys.exit()
args.duplication = round(args.duplication*100, 1)

# Packet reordering
args.reordering = float(args.reordering) # Convert to float
if (args.reordering < 0.0 or args.reordering > 1.0):
	print("Invalid argument for 'reordering': Needs to be in the range of 0.0 and 1.0. You said: " + args.reordering)
	sys.exit()
args.reordering = round(args.reordering*100, 1)

# Everything is OK:
print("Simulating:\n{}% packet loss\n{}% packet duplication\n{}% packet reordering\n{}ms latency\n{}ms latency spikes".format(args.loss, args.duplication, args.reordering, args.ping, args.spike))
print(args)
#os.system("iptables -A INPUT -m statistic -p tcp --mode random --probability 0.5 -j DROP")

#cmd = "sudo tc qdisc add dev {} root netem delay {}ms {}ms 50% loss {}% 50% duplicate {}% corrupt {}% reorder {}% 50%".format(args.interface, str(args.ping), str(args.spike), str(args.loss), str(args.duplication), str(args.corruption), str(args.reordering))
cmd = "sudo tc qdisc add dev {} root netem delay {}ms {}ms loss {}% duplicate {}% reorder {}% distribution normal".format(args.interface, str(args.ping), str(args.spike), str(args.loss), str(args.duplication), str(args.reordering))
print("Running command: " + cmd)
os.system(cmd)
