# Randomizer [![Project Status](http://stillmaintained.com/vrillusions/randomizer.png)](http://stillmaintained.com/vrillusions/randomizer)

This is an python/ncurses based script that takes a list of items and randomly assigns a point to each item.  The one to reach the target number first wins.

This was created when at work we were trying to decide on a place to have lunch.  Since no one could think of anything I made this to do the thinking for us.  It purposely takes a minute or two (you need adjust the target number based on your computer speed) to allow anticipation of who's going to win.

## Features

* Creates suspense by slowly counting up to a number instead of instantly picking something.
* The target number changes with the number of items added so it always last around the same time.

## Caveats

* The base target number is hard coded, and some machines run much faster than others.
* This was one of the first python scripts I made, so it needs to be refactored now that I know how to do things properly.
