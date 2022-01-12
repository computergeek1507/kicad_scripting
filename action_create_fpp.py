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
		pinValues = []

		newFile = filename + '.json'
		f = open(newFile, "w")

		for module in board.GetModules():
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
					netName = netName.replace("_", "-")#pocketbeagle library netnames are close
					netName = netName.replace("B", "P8-")#bbb library netnames are not right
					netName = netName.replace("C", "P9-")#bbb library netnames are not right
					if len(netName) == 4:
						netName = netName.replace("-", "-0")
					pinValues.insert(iPin, netName)
		for pin in pinValues:

			f.write("        {  \"pin\": \"")
			f.write(pin)
			f.write("\" },\n")

		f.close()


		wx.MessageBox("Created FPP Pins at \n{}".format(newFile))

CreateFPPJSON().register()