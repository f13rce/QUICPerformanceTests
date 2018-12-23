# Necessary imports
import os
import time
import subprocess
from subprocess import check_output

# Edit these variables:
clientDir = "/path/to/chromium/src/out/Debug/quic_client"
startingTest = 0 # Test ID to start, leave 0 if you want to start from the first test
sampleSize = 1 # If you want to level out the randomness, increase this number. Note that this will affect the time taken to get one test done

# Change these if you want to test other alterations
interface = "lo"
losses = [0.001, 0.25, 0.33, 0.5]
reorderings = [0.001, 0.25, 0.33, 0.5]
duplications = [0.001, 0.25, 0.33, 0.5]
pings = [1, 100, 250, 500, 1250]
spikes = [1, 100, 250, 500, 1250]

contents = ["10kb", "1mb"] # Page sizes processed in changecontent.py

# Conveniences, change if you prefer something else
file = "./captureudp.sh"
process = "udp.capture"
capName = "packets.pcap"

# Start of script
def Browse():
	try:
		command = "{} --host=127.0.0.1 --port=6121 https://www.example.org/ > /dev/null".format(clientDir)
		result = check_output([command],shell=True)
		result = result.decode("utf-8")
		result = str(result)
		if (result == ""):
			#print("Browsing was a success!")
			return True
		else:
			print("Browsing failed: " + result)
			return False
	except:
		return False

def GetTime():
	millis = int(round(time.time() * 1000))
	return millis

GREEN='\033[0;32m'
NC='\033[0m'
def PrintColoredLine(text):
        lines = "--------------------------------------------------------------"
        os.system("\n")
        os.system("echo \"" + GREEN + lines + "\"")
        os.system("echo \">>> " + GREEN + text + " <<<\"")
        os.system("echo \"" + GREEN + lines + NC + "\"")
        os.system("\n")

def GetMessageCount():
	try:
		command = "tcpdump -r packets.pcap 2>/dev/null | wc -l; true"
		result = check_output([command],shell=True)
		result = result.decode("utf-8")
		#print("Message count: " + result)
		return int(str(result).rstrip())
	except:
		return 0

def GetBandwidth():
	try:
		#command = "tcpdump -r packets.pcap | awk '{ sum += $8 } END { print sum }'; true"
		command = "wc -c < packets.pcap; true"
		result = check_output([command],shell=True)
		result = result.decode("utf-8")
		#print("Bandwidth: " + result)
		return int(str(result).rstrip())
	except:
		return 0

def Log(text):
	try:
		text += "\n"
		with open("log".format(content), "a") as myfile:
			print("[LOG]: {}".format(text))
			myfile.write(text)
	except:
		return

i = 0

totalTests = len(losses) * len(reorderings) * len(duplications) * len(pings) * len (spikes) * len(contents)
simulateTime = 0.5
currentTest = 0

for content in contents:
	os.system("python3 changecontent.py -s {}".format(content))

	for loss in losses:
		for reorder in reorderings:
			for duplication in duplications:
				for ping in pings:
					for spike in spikes:
						try: # Can never be too careful, don't want the test to break suddenly
							currentTest += 1

							if (currentTest < startingTest):
								Log("Skipping... {}/{}".format(currentTest, startingTest))
								continue

							PrintColoredLine("Running test {}/{}: {} [{}% loss, {}% duping, {}ms ping, {}ms spike, {}% reordering]...".format(currentTest, totalTests, content, loss, duplication, ping, spike, reorder))
							Log("Running test {}/{} - {}".format(currentTest, totalTests, content))

							# Refresh headers so that they don't time out or expire
							if (currentTest % 5 == 0):
								print("Restoring headers to ensure integrity")
								os.system("python3 changecontent.py -s {}".format(content))

							# Start simulations
							cmd = "python simulatenetwork.py -i {} -l {} -p {} -s {} -d {} -r {}".format(interface, loss, ping, spike, duplication, reorder)
							print("Running command: {}".format(cmd))
							os.system(cmd)

							# Run tests
							i = 0
							totalTime = 0
							fails = 0
							messageCount = 0
							bandwidth = 0
							while (i < sampleSize):
								# Reset
								os.system("sudo rm {}".format(capName))
								os.system("touch {}".format(capName))

								# Start UDP capture
								os.system("screen -S {} -d -m \"{}\"".format(process, file))
								time.sleep(simulateTime)
								#os.system("{}".format(file))

								# Start timer
								start = GetTime()
								success = Browse()

								# Store result
								if (success):
									end = GetTime()

									# Stop capturing
									#print("Stopping packet capture")
									os.system("screen -X -r {} quit".format(process))
									time.sleep(simulateTime)

									# Print result
									i += 1
									print("{}: {}ms".format(i, end - start))
									totalTime += (end - start)
									Log("Test succeeded!")

									#print("Analyzing packet capture:")
									messageCount += GetMessageCount()
									bandwidth += GetBandwidth()
								else:
									# Stop capturing
									#print("Stopping packet capture")
									Log("Test failed. Retrying...")
									os.system("screen -X -r {} quit".format(process))
									time.sleep(simulateTime)
									fails += 1

							# Save results
							print("Storing results")
							with open("results/{}.csv".format(content), "a") as resultsFile: # Will be stored as "10kb.csv", etc.
								toWrite = "{},{},{},{},{},{},{},{},{},{}\n".format(currentTest, totalTime * 5, messageCount * 5, bandwidth * 5, loss, duplication, ping, spike, reorder, fails)
								print("Writing: {}".format(toWrite))
								resultsFile.write(toWrite)

							# Restore simulations
							print("Stopping network simulations")
							os.system("sudo ./restorenetwork.sh")
							time.sleep(simulateTime)
							print("Done with this sample")
						except:
							log("ERROR: Some exception happened :( will continue to the next test.")
							continue

