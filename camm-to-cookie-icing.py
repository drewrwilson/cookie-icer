# Based on Two stage example Virtual Machine file by Nadya Peek Dec 2014
# moves get set in Main
# usb port needs to be set in initInterfaces

#------IMPORTS-------
from pygestalt import nodes
from pygestalt import interfaces
from pygestalt import machines
from pygestalt import functions
from pygestalt.machines import elements
from pygestalt.machines import kinematics
from pygestalt.machines import state
from pygestalt.utilities import notice
from pygestalt.publish import rpc	#remote procedure call dispatcher
import time
import io

import sys # this is so we can read a parameter

#------READ FILENAME AS PARAMETER------
if (len(sys.argv) > 1):
    filename = sys.argv[1]
else:
    filename = 'example-shapes.camm' # If no filename set, use this example name



#------VIRTUAL MACHINE------
class virtualMachine(machines.virtualMachine):

	def initInterfaces(self):
		if self.providedInterface: self.fabnet = self.providedInterface		#providedInterface is defined in the virtualMachine class.
		else: self.fabnet = interfaces.gestaltInterface('FABNET', interfaces.serialInterface(baudRate = 115200, interfaceType = 'ftdi', portName = '/dev/tty.usbserial-FTSJZKOC'))

	def initControllers(self):
		self.xAxisNode = nodes.networkedGestaltNode('X Axis', self.fabnet, filename = '086-005a.py', persistence = self.persistence)
		self.yAxisNode = nodes.networkedGestaltNode('Y Axis', self.fabnet, filename = '086-005a.py', persistence = self.persistence)

		self.xyNode = nodes.compoundNode(self.xAxisNode, self.yAxisNode)

	def initCoordinates(self):
		self.position = state.coordinate(['mm', 'mm'])

	def initKinematics(self):
		self.xAxis = elements.elementChain.forward([elements.microstep.forward(4), elements.stepper.forward(1.8), elements.leadscrew.forward(8), elements.invert.forward(True)])
		self.yAxis = elements.elementChain.forward([elements.microstep.forward(4), elements.stepper.forward(1.8), elements.leadscrew.forward(8), elements.invert.forward(False)])
		self.stageKinematics = kinematics.direct(2)	#direct drive on all axes

	def initFunctions(self):
		self.move = functions.move(virtualMachine = self, virtualNode = self.xyNode, axes = [self.xAxis, self.yAxis], kinematics = self.stageKinematics, machinePosition = self.position,planner = 'null')
		self.jog = functions.jog(self.move)	#an incremental wrapper for the move function
		pass

	def initLast(self):
		#self.machineControl.setMotorCurrents(aCurrent = 0.8, bCurrent = 0.8, cCurrent = 0.8)
		#self.xNode.setVelocityRequest(0)	#clear velocity on nodes. Eventually this will be put in the motion planner on initialization to match state.
		pass

	def publish(self):
		#self.publisher.addNodes(self.machineControl)
		pass

	def getPosition(self):
		return {'position':self.position.future()}

	def setPosition(self, position  = [None]):
		self.position.future.set(position)

	def setSpindleSpeed(self, speedFraction):
		#self.machineControl.pwmRequest(speedFraction)
		pass

#------IF RUN DIRECTLY FROM TERMINAL------
if __name__ == '__main__':
	# The persistence file remembers the node you set. It'll generate the first time you run the
	# file. If you are hooking up a new node, delete the previous persistence file.
	stages = virtualMachine(persistenceFile = "test.vmp")

	# You can load a new program onto the nodes if you are so inclined. This is currently set to
	# the path to the 086-005 repository on Nadya's machine.
	#stages.xyNode.loadProgram('../../../086-005/086-005a.hex')

	# This is a widget for setting the potentiometer to set the motor current limit on the nodes.
	# The A4982 has max 2A of current, running the widget will interactively help you set.
	#stages.xyNode.setMotorCurrent(0.7)

	# This is for how fast the
	stages.xyNode.setVelocityRequest(8)

	# Read moves from file

	# Open a .camm file created with the fab modules from an SVG
	# This file is in HPGL format, a simple text file with
	# PU (pen up) and PD (pen down commands)
	# Each command is followed by an x,y coordinate to move to
	# and delimited with semicolons. This reads all lines into one string.

	with open(filename, 'r') as myfile:
	    data="".join(line.rstrip() for line in myfile)

	# Split the string into a list of individual commands

	commands = data.split(";")

	# For each command in the list, get the command
	# (i.e. PU or PD, ignoring everything else)
	# and the x, y coordinates
	moves = []

	for command in commands:


	    # Using python string operations, get first two characters

	    c = command[0:2]

	    # Get everything after character 2 as a string

	    coords = command[2:]

	    # Split it into a list of coordinates

	    coordlist = coords.split(",")

	    # Take the x and coordinates

	    x = coordlist[0]
	    y = coordlist[-1]

	    # Now do something with those commands and numbers
	    # These prints can be replaced with gestalt commands

	    #append the coordinates to array


	    if (c == "PU") or (c == "PD"):
	        tempcoord = []
	        #x = int(x)
	        #y = int(y)
	        tempcoord.append(int(x))
	        tempcoord.append(int(y))
	        tempcoord.append(c)
	        moves.append(tempcoord)

	# Moves from file
	# moves = [[10,10],[20,20],[10,10],[0,0]]

	# Move!
	for move in moves:
		justmovecoords = move[0:2] #remove the PU/PD
		stages.move(justmovecoords, 0)
		status = stages.xAxisNode.spinStatusRequest()
		# This checks to see if the move is done.
		while status['stepsRemaining'] > 0:
			time.sleep(0.001)
			status = stages.xAxisNode.spinStatusRequest()
