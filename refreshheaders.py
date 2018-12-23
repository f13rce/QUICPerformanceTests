import os
import sys

originalDir = os.getcwd()

# Get newest headers - https://www.chromium.org/quic/playing-with-quic
GREEN='\033[0;32m'
NC='\033[0m'

def PrintColoredLine(text):
	lines = "--------------------------------------------------------------"
	os.system("\n")
	os.system("echo \"" + GREEN + lines + "\"")
	os.system("echo \">>> " + GREEN + text + " <<<\"")
	os.system("echo \"" + GREEN + lines + NC + "\"")
	os.system("\n")

PrintColoredLine("Removing old headers...")

# Start from fresh and remove the old headers
os.system("rm -r /tmp/quic-data/www.example.org")

# Download the latest headers and move it into the /tmp/quic-data/ dir
PrintColoredLine("Downloading latest headers...")

os.system("cd {} && wget -p --save-headers https://www.example.org".format(originalDir))
os.system("mv www.example.org/ /tmp/quic-data/")

#sys.exit(0)

PrintColoredLine("Reading new header contents...")

# Read out newest headers, copy them to replace the old ones
headers = ""
addedQuicHeader = False
quicHeader = "X-Original-Url: https://www.example.org/" + '\n'

with open("/tmp/quic-data/www.example.org/index.html") as f:
	content = f.readlines()
	content = [x.strip() for x in content]
	for line in content:
		if (line == ""): # Headers stop at an empty line, so we know this is the end
			break
		else:
			if (("Transfer-Encoding: chunked" not in line) and ("Alternate-Protocol:" not in line) and ("Content-Length" not in line)):
				# Ensure quic header is inserted in a somewhat-normal place
				if ((not addedQuicHeader) and ("X-Cache" in line)):
					headers += quicHeader
					addedQuicHeader = True

				headers += line + '\n'

			# A line we must remove from the headers
			else:
				print("Ignoring header line: {}".format(line))
			#print(line)

# Add the QUIC required header if it wasn't added yet
if (not addedQuicHeader):
	headers += quicHeader
	addedQuicHeader = True

headers += '\n'

print("Headers:\n{}".format(headers))

PrintColoredLine("Replacing old headers...")

# Replace headers
files = ["10kb", "100kb", "1mb", "10mb"]
print("Files to edit: {}".format(files))

for file in files:
	PrintColoredLine("Replacing headers from file {}.html...".format(file))
	strippedHeaders = False
	newContent = headers

	# Read file and ignore the headers, then rewrite the file
	fileLoc = "/tmp/quic-data/{}.html".format(file)
	print("Opening {} for reading...".format(fileLoc))
	os.system("file {}".format(fileLoc))
	with open(fileLoc, encoding = "ISO-8859-1") as f:
		content = f.readlines()
		content = [x.strip() for x in content]

		for line in content:
			if (not strippedHeaders):
				if (line == ""):
					strippedHeaders = True
			else:
				newContent += line + '\n'

	#print(newContent) # WARNING: This will look retarded in the terminal due to the encoding
	newFile = open(fileLoc + ".replaced", 'w')
	newFile.write(newContent)
	newFile.close()

PrintColoredLine("Refreshing certificates...")
os.system("cd /home/islotboom/quic/chromium/src/net/tools/quic/certs/ && sudo ./generate-certs.sh")
os.system("cd {}".format(originalDir))

PrintColoredLine("All done!")
