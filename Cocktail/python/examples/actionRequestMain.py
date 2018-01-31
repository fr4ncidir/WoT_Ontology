#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  actionRequestMain.py
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
import sys
sys.path.append("../")

import colorama
import rlcompleter,readline
from colorama import Fore, Style
from webthing import *
from wot_init import *

logging.basicConfig(format=LOGFORMAT,level=LOGLEVEL)

subid = ""
kp = None

class ConfirmationHandler:
	def __init__(self):
		pass
	def handle(self, added, removed):
		global kp
		global subid
		for item in added:
			logging.info("Action Confirmation handler: {} timestamp received".format(item["timestamp"]["value"]))
			try:
				kp.unsubscribe(subid,False)
			except Exception:
				pass

class ActionCompleter(object):  # Custom completer
	def __init__(self, options):
		self.options = sorted(options)
	def complete(self, text, state):
		if state == 0:  # on first trigger, build possible matches
			if text:  # cache matches (entries that start with entered text)
				self.matches = [s for s in self.options if s and s.startswith(text)]
			else:  # no text entered, all matches possible
				self.matches = self.options[:]
		# return match indexed by state
		try: 
			return self.matches[state]
		except IndexError:
			return None

def main(args):
	global kp
	global subid
	
	thing_action_map = {}
	action_names = []
	jsap_obj = JSAPObject.JSAPObject(JSAP)
	colorama.init()
	
	while True:
		# discovery things available
		web_things = WebThing.discoveryThings(jsap_obj)
		for item in web_things:
			print("{}WEBTHING: {}".format(Fore.RED,item["thing"]["value"]))
			for action in Action.getActionList(jsap_obj,item["thing"]["value"]):
				print("{}\tACTION: {}".format(Fore.GREEN,action["aName"]["value"]))
				thing_action_map[action["aName"]["value"]] = (item["thing"]["value"],action["action"]["value"],action["inDataSchema"]["value"])
				action_names.append(action["aName"]["value"])
			for event in Event.getEventList(jsap_obj,item["thing"]["value"]):
				print("{}\tEVENT: {}".format(Fore.YELLOW,event["eName"]["value"]))
			for propert in Property.getPropertyList(jsap_obj,item["thing"]["value"]):
				print("{}\tPROPERTY: {} (value: {}){}".format(Fore.MAGENTA,propert["pName"]["value"],propert["pValue"]["value"],Fore.RESET))
		if len(web_things)==0:
			print("No webthing was found!")
			return 0
		else:
			break
	
	completer = ActionCompleter(action_names)
	readline.set_completer(completer.complete)
	readline.parse_and_bind("tab: complete")
	
	if len(action_names)==0:
		print("No actions to be called!")
		return 0
	else:
		while True:
			try:
				print("Write the name of the action you want to call: ")
				action_name = input()
				if action_name in thing_action_map:
					instance = "wot:{}".format(uuid4())
					kp,subid = Action.waitActionConfirmation(jsap_obj,instance,ConfirmationHandler())
					if thing_action_map[action_name][2]!="":
						print("Required input with format:\n{}".format(action["inDataSchema"]["value"]))
						print("Please insert input:")
						myActionInput = input()
					else:
						myActionInput = None
					Action.askForAction(jsap_obj,thing_action_map[action_name][0],thing_action_map[action_name][1],input_value=myActionInput,instanceUri=instance)
				else:
					logging.error("{}: Unknown action name".format(action_name))
			except KeyboardInterrupt:
				print("CTRL-C pressed! Bye!")
				try:
					kp.unsubscribe(subid,False)
				except Exception:
					pass
				return 0

if __name__ == '__main__':
	sys.exit(main(sys.argv))

