import sys # this is so we can read a parameter

if (len(sys.argv) > 1):
    filename = sys.argv[1]
else:
    filename = 'example-shapes.camm'


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
allcoords = []

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
        allcoords.append(tempcoord)

for thiscoord in allcoords:
    print thiscoord
