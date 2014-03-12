#!/usr/bin/env python
# encoding: utf-8
"""
Midi volume pedal with midi learn function. 
Copyleft Jean-Emmanuel Doucet
Released under GNU/GPL License (http://www.gnu.org/)
"""

#Imports

from pyo import *
import wx, sys, getopt

#Arguments handling

mididevice = pm_get_input_devices()[1][0]
ctlnumber = 0
stereo = 0

def main(argv):
	global mididevice, ctlnumber, stereo
	license = "Midi volume pedal with midi learn function.\nCopyleft Jean-Emmanuel Doucet\nReleased under GNU/GPL License (http://www.gnu.org/)"
	help = "Usage : python volumePedal.py [OPTIONS]\n\nOptions :\n -d, --device  X\tmidi input device number\n -c, --control X\tmidi control number\n -s, --stereo\t\tstereo mode (2 channels controled by one pedal)\n -h, --help\t\tshow this help"
	devices = pm_get_input_devices()
	try:
		opts, args = getopt.getopt(argv,"hsd:c:",["sstereo","ddevice=","ccontrol="])
	except getopt.GetoptError:
		print "Error : something went wrong !" + "\n\n" + help + "\n\nAvailables midi input devices :"
		for i in range(len(devices[1])):
			print " [ %d ] >>> %s " % (devices[1][i], devices[0][i])
		sys.exit()
	for opt, arg in opts:
		if opt in ("-h", "--hhelp"):
			print license + "\n\n" + help + "\n\nAvailables midi input devices :"
			for i in range(len(devices[1])):
				print " [ %d ] >>> %s " % (devices[1][i], devices[0][i])
			sys.exit()
		elif opt in ("-s", "--sstereo"):
			stereo = 1
		elif opt in ("-d", "--ddevice"):
			mididevice = int(arg)
		elif opt in ("-c", "--ccontrol"):
			ctlnumber = int(arg)
	
	ok=0
	for i in range(len(pm_get_input_devices()[1])):
		if pm_get_input_devices()[1][i] == mididevice:
			print "Midi device \t: [ %d ] >>> %s " % (pm_get_input_devices()[1][i], pm_get_input_devices()[0][i])
			print "Control number \t: [ %d ]" %ctlnumber
			ok = 1
	if ok !=1:
		print "Error : wrong midi input device !" + "\n\n" + help + "\n\nAvailables midi input devices :"
		for i in range(len(devices[1])):
			print " [ %d ] >>> %s " % (devices[1][i], devices[0][i])
		sys.exit()
if __name__ == "__main__":
	main(sys.argv[1:])


#Volume Pedal Classes

class volumePedal:
	def __init__(self, ctlnumber=0, exp=1, stereo=0):
		self.ctlnumber = ctlnumber
		self.exp = exp
		self.chnl = range(stereo+1)
		
		self.midiScan =  CtlScan(self.setMidiCtlNumber, toprint=False).stop()
		
		self.getMidi = Midictl(ctlnumber=self.ctlnumber, minscale=0, maxscale=127, init=0, channel=0, mul=1, add=0)
		self.getMidi.setInterpolation(0)
		
		self.scaleMidi = Scale(input=self.getMidi, inmin=0, inmax=127, outmin=-0.01, outmax=1, exp=self.exp, mul=1, add=0)
		
		self.smooth = Port(input=self.scaleMidi, risetime=0.005, falltime=0.005, init=0, mul=1, add=0)
		
		self.volume = Max(self.smooth,0)
		
		#self.audio = Sine(freq=[500,600],mul=self.volume).play() #debug
		self.audio = Input(chnl=self.chnl, mul=self.volume, add=0)
		
		self.frame = volumePedalFrame(volumePedal=self)
		
		self.trigChange = Change(self.scaleMidi)
		self.funcChange = TrigFunc(self.trigChange,self.setFrameValue)
		
	def get(self):
		return self
		
	def getOut(self):
		return self.audio
		
	def out(self):
		self.audio.out()
		
	def ctrl(self, main=0):
		self.frame.Show()
		
	def setFrameValue(self):
		value = self.volume.get()
		self.frame.setValue(value)
		#print value #debug
		
	def midiLearn(self):
		self.midiScan.play()

	def setMidiCtlNumber(self, ctlnumber):
		self.getMidi.setCtlNumber(ctlnumber)
		self.frame.setMidiCtlNumber(ctlnumber)
		self.midiScan.stop()
		
	def cancelMidiLearn(self):
		self.midiScan.stop()
		
class volumePedalFrame(wx.Frame):
	def __init__(self, parent=None, title='Volume Pedal', pos=(100,100), size=(100,460), volumePedal=None):
		self.volumePedal = volumePedal
		self.app = wx.App()
		wx.Frame.__init__(self, parent, id=wx.ID_ANY, title=title, pos=pos, size=size)
		
		self.panel = wx.Panel(self)
		self.panel.SetBackgroundColour("#DDDDDD")

		self.gauge = wx.Gauge(self.panel, id=-1, range=1000, pos=(20,20), size=(60,360), style=wx.GA_VERTICAL)
		
		self.ctlNumber = wx.StaticText(self.panel, id=-1, label="MIDI CC", pos=(22,390), size=(60,20))
		self.setCtlNumber =  wx.Button(self.panel, id=-1, label="Learn", pos=(20, 410), size=(60,30), style=wx.ALIGN_LEFT)
		if self.volumePedal.getMidi.ctlnumber !=0:
			self.setCtlNumber.SetLabel("%.0f" %self.volumePedal.getMidi.ctlnumber)
		
		self.setCtlNumber.Bind(wx.EVT_BUTTON, self.midiLearn)
		

	def setValue(self,value):
		wx.CallAfter(self.deferSetValue, value)
		
	def deferSetValue(self,value):
		self.gauge.SetValue(round(value*1000))

		
	def midiLearn(self,evt):
		if	self.setCtlNumber.Label == "...":
			self.setCtlNumber.SetLabel("%.0f" %self.volumePedal.getMidi.ctlnumber)
			self.volumePedal.cancelMidiLearn()
		else:	
			self.setCtlNumber.SetLabel("...")
			self.volumePedal.midiLearn()
		
	def setMidiCtlNumber(self, ctlnumber):
		self.setCtlNumber.SetLabel("%.0f" %ctlnumber)


#Server Init

s = Server(nchnls=stereo+1, audio='jack', jackname='Volume Pedal')
s.setJackAuto(xin=False, xout=False)

s.setMidiInputDevice(mididevice)
s.boot()
s.start()

#Volume Pedal Init

vp = volumePedal(ctlnumber=ctlnumber,stereo=stereo).get()
vp.ctrl()
vp.out()


vp.frame.app.MainLoop()
