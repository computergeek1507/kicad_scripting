import pcbnew
import os
import wx

#from pcbnew import *

# > V5.1.5 and V 5.99 build information
if hasattr(pcbnew, 'GetBuildVersion'):
	BUILD_VERSION = pcbnew.GetBuildVersion()
else:
	BUILD_VERSION = "Unknown"

class Fix3DModels(pcbnew.ActionPlugin):

	def defaults(self):
		self.name = "Update 3D v5 Models Paths"
		self.category = "Scott Plugin"
		self.description = "Update v5 3D Models Paths to v6"

	def Run(self):
		board = pcbnew.GetBoard()

		for footprint in board.GetFootprints():
			ref = footprint.GetReference()
			models = footprint.Models()
			for i in range(len(models)):
				file = models[i].m_Filename
				models[i].m_Filename = models[i].m_Filename.replace("${KISYS3DMOD}", "${KICAD6_3DMODEL_DIR}")
				models[i].m_Filename = models[i].m_Filename.replace("Diodes_SMD", "Diode_SMD")
				# wx.MessageBox(model.m_Filename)
				# print(f"{ref}: {models[i].m_Filename}")
			
		pcbnew.Refresh() 
		wx.MessageBox("Update 3D v5 Models Paths, maybe")

Fix3DModels().register()