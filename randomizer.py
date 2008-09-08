#!/usr/bin/env python
# vim:ts=4:sw=4:ft=python:fileencoding=utf-8
"""Randomizer

Takes a list and randomly chooses an item

keys supported:
q - quit application
s - stops execution and just shows latest list
r - resumes processing

todo: be able to handle a list that extends the length of the window.  It will
error out if the length exceeds the screen right now.
"""

# $Id$
__version__ = "$Rev$"

import curses, curses.wrapper
import sys, random, os, math, string
import time
import traceback
from operator import itemgetter
from optparse import OptionParser


class gb:
	"""Global Variables"""
	items = {}
	displayLimit = 100
	baseLimit = 200000 # this divided # of items is the final limit
	limit = 0
	displayCount = 0
	pw = None
	filename = 'list.txt'
	#stdscrn = None # will point to Curses window object 


class Pinwheel:
    """Displays the pinwheel at the top of the page
    
    It will always display on second line"""
    
    def __init__(self):
        self.stdscr = None  #set this to the stdscr object
        self.index = 0
        self.img = ['/', '-', '\\', '|', '/', '-', '\\', '|']
        self.curCount = 0
        self.barLength = 20
        
    def display(self):
        """Increments the index and displays the next image"""
        self.progress = float(self.curCount) / float(gb.limit)
        self.barDoneLength = math.floor(self.barLength * self.progress)
        if self.barDoneLength < 0:
            self.barDoneLength = 0
        self.barDone = '#' * int(self.barDoneLength)
        self.barNotDone = '-' * int(self.barLength - self.barDoneLength)
        self.percentage = int(math.floor(self.progress * 100))
        self.line = ' ' + self.img[self.index] + ' '
        self.line = self.line + '[' + self.barDone + self.barNotDone + '] ' + str(self.percentage) + '%'
        self.index = self.index + 1
        if self.index >= len(self.img):
            self.index = 0
        self.stdscr.move(1, 0)
        self.stdscr.addstr(self.line)
        self.stdscr.move(0, 0)
        #self.stdscr.refresh()


def restoreScreen(stdscr):
    """Returns terminal to a usable state
    
    @param stdscr the curses screen"""
    curses.nocbreak()
    stdscr.keypad(0)
    curses.echo()


def centerText(stdscr, text):
    """Centers text horizontally
    
    Cursor should already be on the proper vertical line
    
    @param stdscr the curses screen
    @param text text to center"""
    offset = (stdscr.getmaxyx()[1] / 2) - (len(text) / 2)
    stdscr.addstr(stdscr.getyx()[0], offset, text + "\n")
    stdscr.refresh()


def printHeader(stdscr):
    """Prints the heading at the top of the page and sets cursor to second line
    
    @param stdscr the curses screen"""
    heading = "          Randomizer          "
    stdscr.move(0, 0)
    if curses.has_colors():
        # we have colors, hooray
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)
        stdscr.addstr(heading, curses.color_pair(1))
    else:
        stdscr.addstr(heading, curses.A_STANDOUT)
    stdscr.addstr('  Winning Score: ' + str(gb.limit))
    stdscr.move(1, 0) 


def doRandomizer(stdscr):
    """The randomization process
    
    This will pick a random item out of a list, increment it's counter by 1 and
    repeats the process.  If displayLimit is reached, it will display the results
    and continue.  If limit is reached, it will display the results and then
    pause so user can see it
    
    @param stdscr the curses screen"""
    gb.displayCount = gb.displayCount + 1
    random.seed(os.urandom(1024))
    item = random.choice(gb.items.keys())  #returns one random item from list
    gb.items[item] = gb.items.get(item, 0) + 1
    if gb.displayCount >= gb.displayLimit: 
        displayItems(stdscr)
    sortedItems = sorted(gb.items.iteritems(), key=itemgetter(1), reverse=True)
    curCount = itemgetter(0)(sortedItems) #returns [value, key]
    if curCount[1] >= gb.limit:
        displayItems(stdscr)
        stdscr.move(5,0)
        centerText(stdscr, ' COMPLETE, press q to quit ')
        stdscr.nodelay(0)


def displayItems(stdscr):
    """Displays listing of items
    
    @param stdscr the curses screen"""
    sortedItems = sorted(gb.items.iteritems(), key=itemgetter(1), reverse=True)
    # the current count is the first item's value
    curCount = itemgetter(0)(sortedItems) #returns [value, key]
    gb.pw.curCount = curCount[1]
    gb.pw.display()
    countPad = len(str(gb.limit))
    linenum = 2
    for itemName, itemCount in sortedItems:
        stdscr.addstr(linenum, 0, string.zfill(str(itemCount), countPad) + ' ' + itemName)
        linenum = linenum + 1
    resetCursor(stdscr)
    stdscr.refresh()


def populateList(stdscr):
    """Populates the list with items from a text file
    
    @param stdscr the curses screen"""
    file = open(gb.filename, 'r')
    for line in file:
        # filter out the commented lines
        if line[0] != '#': gb.items[line] = 0
    gb.limit = int(math.floor(gb.baseLimit / len(gb.items)))


def resetCursor(stdscr):
    """resets the cursor to the 0, 0 spot so it isn't jumping all over the place
    
    @param stdscr the curses screen"""
    stdscr.move(0,0)


def main(stdscr):
    """The main function that runs everything
    
    @param stdscr the curses screen returned via wrapper function
    @param argv command arguments"""
    populateList(stdscr)
    resetCursor(stdscr)
    stdscr.refresh()
    curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLUE)
    stdscr.nodelay(1)    # don't want the getch() below to stop things
    stdscr.leaveok(1)
    printHeader(stdscr)
    resetCursor(stdscr)
    gb.pw = Pinwheel()
    gb.pw.stdscr = stdscr
    while True:
        doRandomizer(stdscr)
        c = stdscr.getch()
        if c == ord('c'): centerText(stdscr, "I am centered")
        elif c == ord('s'): 
            #allow getch to halt again
            stdscr.nodelay(0)
        elif c == ord('r'): 
            #continue on
            stdscr.nodelay(1)
        elif c == ord('q'): break    # Exit the while()
        elif c == curses.KEY_HOME: x = y = 0
    restoreScreen(stdscr);


if __name__ == '__main__':
    # process arguments before running screen in case they want help    
    parser = OptionParser()
    parser.add_option('-l', '--list', default=gb.filename,
        help="use list FILE (default: " + gb.filename + ')', metavar='FILE')
    (options, args) = parser.parse_args()
    
    gb.filename = options.list
    
    try:
        # run the program inside a wrapper to catch errors nicely
        curses.wrapper(lambda stdscr: main(stdscr))
    except KeyboardInterrupt, e:
        # Ctrl-c
        raise e
    except SystemExit, e:
        # sys.exit()
        raise e
    except Exception, e:
        print "ERROR, UNEXPECTED EXCEPTION"
        print str(e)
        traceback.print_exc()
        sys.exit(1)
    else:
        # Main function is done, exit cleanly
        sys.exit(0)
