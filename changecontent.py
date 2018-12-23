import argparse
import os

# Main
parser = argparse.ArgumentParser()

# python3 test_smb.py -d /sne/home/USER/smb-nfs-performance/10kbfiles -s IPADDRESS -u USER -p PASSWORD -o 10kbfilestest -n 10kbtest
parser.add_argument("-s", "--size", help="Size of the new content (Options: 10kb, 100kb, 1mb, 10mb)", required=True)

args = parser.parse_args()

# Verify argument
if (args.size != "10kb" and args.size != "100kb" and args.size != "1mb" and args.size != "10mb"):
	print("Invalid size! This size is not specified. Type --help or -h for info.");

# Everything is OK:
else:
	os.system("python3 refreshheaders.py")

	origin = "/tmp/quic-data"
	site = "www.example.org"

	print("Copying {}/{}.html.replaced to {}/{}/index.html...".format(origin, args.size, origin, site))
	os.system("cp {}/{}.html.replaced {}/{}/index.html".format(origin, args.size, origin, site))

	print("Restarting server so that it loads the new content...")
	os.system("./screenserver.sh")

	print("Done!")
