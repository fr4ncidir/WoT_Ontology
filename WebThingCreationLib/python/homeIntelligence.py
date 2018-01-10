#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  homeIntelligence.py
#  
#  Copyright 2017 Francesco Antoniazzi <francesco.antoniazzi@unibo.it>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  


def main(args):
	# Before: get informations about the environment
	web_things = WebThing.discoveryThings(JPAR,JSAP)
	actions = 
	
	# First step: setup of preferences
	web_things = WebThing.discoveryThings(JPAR,JSAP)
	for item in web_things:
		print("{}WEBTHING: {}".format(Fore.RED,item["thing"]["value"]))
		for action in Action.getActionList(JPAR,JSAP,item["thing"]["value"]):
			print("{}\tACTION: {}".format(Fore.GREEN,action["aName"]["value"]))
			thing_action_map[action["aName"]["value"]] = (item["thing"]["value"],action["action"]["value"],action["inDataSchema"]["value"])
			action_names.append(action["aName"]["value"])
		for event in Event.getEventList(JPAR,JSAP,item["thing"]["value"]):
			print("{}\tEVENT: {}".format(Fore.YELLOW,event["eName"]["value"]))
		for propert in Property.getPropertyList(JPAR,JSAP,item["thing"]["value"]):
			print("{}\tPROPERTY: {} (value: {}){}".format(Fore.MAGENTA,propert["pName"]["value"],propert["pValue"]["value"],Fore.RESET))
	
	# Second step: subscription to ambient variables
	
	# Third step: identification of the problem
	
	# Fourth step: identification of the device and the action
	return 0

if __name__ == '__main__':
	import sys
	sys.exit(main(sys.argv))
