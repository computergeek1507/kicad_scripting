import pcbnew
import os
import wx

#from pcbnew import *

# > V5.1.5 and V 5.99 build information
if hasattr(pcbnew, 'GetBuildVersion'):
	BUILD_VERSION = pcbnew.GetBuildVersion()
else:
	BUILD_VERSION = "Unknown"

def WriteDXFHeader( f):
	f.write("0\n")
	f.write("SECTION\n")
	f.write("2\n")
	f.write("ENTITIES\n")

def WriteDXFFooter( f):
	f.write("0\n")
	f.write("ENDSEC\n")
	f.write("0\n")
	f.write("EOF\n")

def WriteDXFCircle( f, x, y, r, l):
	f.write("0\n")
	f.write("CIRCLE\n")
	f.write("8\n")
	f.write("{0:d}\n".format(l))
	f.write("10\n")
	f.write("{:.6f}\n".format(x))
	f.write("20\n")
	f.write("{:.6f}\n".format(-y))
	f.write("30\n")
	f.write("0\n")
	f.write("40\n")
	f.write("{:.6f}\n".format(r))

def WriteDXFLine( f, x1, y1, x2, y2, l):
	f.write("0\n")
	f.write("LINE\n")
	f.write("8\n")
	f.write("{0:d}\n".format(l))
	f.write("10\n")
	f.write("{:.6f}\n".format(x1))
	f.write("20\n")
	f.write("{:.6f}\n".format(-y1))
	f.write("30\n")
	f.write("0\n")
	f.write("11\n")
	f.write("{:.6f}\n".format(x2))
	f.write("21\n")
	f.write("{:.6f}\n".format(-y2))
	f.write("31\n")
	f.write("0\n")

def DrawDXFBox( f, x1, y1, x2, y2, l):
	WriteDXFLine(f,x1,y1,x2,y1,l)
	WriteDXFLine(f,x1,y1,x1,y2,l)
	WriteDXFLine(f,x2,y1,x2,y2,l)
	WriteDXFLine(f,x1,y2,x2,y2,l)

class CreateDXF(pcbnew.ActionPlugin):

	def defaults(self):
		self.name = "Create DXF File"
		self.category = "DXF Plugin"
		self.description = "Create .dxf file with dementions"

	def Run(self):
		board = pcbnew.GetBoard()
		os.chdir(os.path.dirname(os.path.abspath(board.GetFileName())))
		filename = os.path.splitext(board.GetFileName())[0]

		description = os.path.splitext(os.path.basename(board.GetFileName()))[0]

		bbox = board.ComputeBoundingBox(True)
		#print "bbox %s %s" % (bbox.GetPosition(), bbox.GetSize())
		min_x = bbox.GetPosition().x
		min_y = bbox.GetPosition().y
		width = pcbnew.ToMils(bbox.GetSize().x)
		height = pcbnew.ToMils(bbox.GetSize().y)

		newDxfFile = filename + '.dxf'
		df = open(newDxfFile, "w")
		WriteDXFHeader(df)

		DrawDXFBox(df,0,0,width,height,0)

		for module in board.GetFootprints():
			ref = module.GetReference()

			#if not ref.startswith( 'R' ) and not ref.startswith( 'J' ) and not ref.startswith( 'K' ) and not ref.startswith( 'D' ) and not ref.startswith( 'C' ):
			#	continue

			for gi in module.GraphicalItems():
				if not gi.GetLayerName().endswith ("Silkscreen"): #only draw slikscreen graphics 
					continue
				gi_bbox = gi.GetBoundingBox()
				gi_width = pcbnew.ToMils(gi_bbox.GetSize().x)
				gi_height = pcbnew.ToMils(gi_bbox.GetSize().y)

				gi_x = pcbnew.ToMils(gi_bbox.GetPosition().x - min_x)
				gi_y = pcbnew.ToMils(gi_bbox.GetPosition().y - min_y)
				DrawDXFBox(df, gi_x, gi_y, gi_x + gi_width, gi_y + gi_height,1)


			if not ref.startswith( 'H' ) : #skip non holes
				continue

			for pad in module.Pads():
				pos = pad.GetPosition()
				pos_x = pcbnew.ToMils(pos.x - min_x)
				pos_y = pcbnew.ToMils(pos.y - min_y)
				pad_size = pcbnew.ToMils(pad.GetSize().y/2) #diameter to radians
				WriteDXFCircle(df, pos_x, pos_y, pad_size,0)

		WriteDXFFooter(df)
		df.close()

		wx.MessageBox("Created .dxf file at \n{}".format( newDxfFile))

CreateDXF().register()