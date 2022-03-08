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
		self.name = "Create FPP JSON Pins"
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

			if val.lower().find("beagle") == -1:
				continue
			for pad in module.Pads():
				m = re.search(reg, pad.GetNet().GetNetname())
				if m:
					iPin = int(m.group(2))
					netName = pad.GetName()
					log.write( str(iPin))
					log.write("\t")
					log.write(netName)
					log.write("\t")
					netName = netName.replace("_", "-")#pocketbeagle library netnames are close
					netName = netName.replace("B", "P8-")#bbb library netnames are not right
					netName = netName.replace("C", "P9-")#bbb library netnames are not right
					if len(netName) == 4:
						netName = netName.replace("-", "-0")
					pinValues[iPin-1] = netName
					log.write(netName)
					log.write("\n")
		#sorted(pinValues)
		for pin in range(len(pinValues)):

			f.write("        {  \"pin\": \"")
			f.write(pinValues[pin])
			f.write("\" },\n")
			log.write( str(pin))
			log.write("\t")
			log.write(pinValues[pin])
			log.write("\n")

		f.close()
		log.close()
		wx.MessageBox("Created FPP Pins at \n{}".format(newFile))

CreateFPPJSON().register()