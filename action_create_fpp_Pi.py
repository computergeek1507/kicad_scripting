import pcbnew
import os
import re
import wx

#from pcbnew import *

# > V5.1.5 and V 5.99 build information
if hasattr(pcbnew, 'GetBuildVersion'):
	BUILD_VERSION = pcbnew.GetBuildVersion()
else:
	BUILD_VERSION = "Unknown"

class CreateFPPJSON(pcbnew.ActionPlugin):

	def defaults(self):
		self.name = "Create FPP JSON Pins Pi"
		self.category = "FPP Plugin"
		self.description = "Create JSON Pins define file for FPP"

	def Run(self):
		board = pcbnew.GetBoard()
		os.chdir(os.path.dirname(os.path.abspath(board.GetFileName())))
		filename = os.path.splitext(board.GetFileName())[0]

		description = os.path.splitext(os.path.basename(board.GetFileName()))[0]

		reg = r"(DATA|OUT)(\d+)"
		pinValues = {}

		newFile = filename + '.json'
		f = open(newFile, "w")

		logFile = filename + '.log'
		log = open(logFile, "w")

		for module in board.GetFootprints():
			ref = module.GetReference()
			desp = module.GetDescription()
			val = module.GetValue()

			if val.lower().find("raspberry_pi") == -1:
				continue
			for pad in module.Pads():
				m = re.search(reg, pad.GetNet().GetNetname())
				if m:
					iPin = int(m.group(2))
					netName = pad.GetNumber()
					log.write( str(iPin))
					log.write("\t")
					log.write(netName)
					log.write("\t")
					netName = "P1-" + netName#pocketbeagle library netnames are close

					pinValues[iPin-1] = netName
					log.write(netName)
					log.write("\n")
		#sorted(pinValues)

		f.write("{\n")
		f.write("    \"name\": \"")
		f.write(description)
		f.write("\",\n")
		f.write("    \"longName\": \"")
		f.write(description)
		f.write("\",\n")
		f.write("    \"driver\": \"DPIPixels\",\n")
		f.write("    \"numSerial\": 0,\n")
		f.write("    \"outputs\": [\n")
		for pin in range(len(pinValues)):

			f.write("        {  \"pin\": \"")
			f.write(pinValues[pin])
			if(pin==len(pinValues)-1):
				f.write("\" }\n")
			else:
				f.write("\" },\n")
			#f.write("\" },\n")
			log.write( str(pin))
			log.write("\t")
			log.write(pinValues[pin])
			log.write("\n")

		f.write("    ],\n")
		f.write("    \"groups\": [\n")
		f.write("        {\n")
		f.write("            \"start\": 1,\n")

		f.write("            \"count\": ")
		f.write(str(len(pinValues)))
		f.write("\n")
		f.write("        }\n")
		f.write("    ]\n")
		f.write("}\n")
		f.close()
		log.close()
		wx.MessageBox("Created FPP Pins at \n{}".format(newFile))

CreateFPPJSON().register()