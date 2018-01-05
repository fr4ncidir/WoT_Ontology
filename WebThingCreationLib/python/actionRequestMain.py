#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  wt_tempSensor.py
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
import colorama
from colorama import Fore, Style
from webthing import *
from wot_init import *

logging.basicConfig(format="%(levelname)s %(asctime)-15s %(message)s",level=LOGLEVEL)

subid = ""
kp = None

class ConfirmationHandler:
	def __init__(self):
		pass
	def handle(self, added, removed):
		for item in added:
			logging.info("Action Confirmation handler: {} timestamp received".format(item["timestamp"]["value"]))
			kp.unsubscribe(subid,False)

def main(args):
	global kp
	global subid
	
	# discovery things available
	for item in WebThing.discoveryThings(JPAR,JSAP):
		print(item["thing"]["value"])
		print(Action.getActionList(JPAR,JSAP,item["thing"]["value"]))
	
	colorama.init()
	
	# while True:
		# print(Fore.RED + "Accendo il riscaldamento? " + Style.RESET_ALL)
		# input()
		# instance = "wot:IstanzaAccendi"
		# kp,subid = Action.waitActionConfirmation(JPAR,JSAP,instance,ConfirmationHandler())
		# Action.askForAction(JPAR,JSAP,"wot:Heater","wot:AccendiRiscaldamento",instanceUri=instance)
		# print(Fore.RED + "Spengo il riscaldamento? " + Style.RESET_ALL)
		# input()
		# instance = "wot:IstanzaSpegni"
		# kp,subid = Action.waitActionConfirmation(JPAR,JSAP,instance,ConfirmationHandler())
		# instance = Action.askForAction(JPAR,JSAP,"wot:Heater","wot:SpegniRiscaldamento",instanceUri=instance)

if __name__ == '__main__':
	import sys
	main(sys.argv)
	while True:
		try:
			pass
		except KeyboardInterrupt:
			kp.unsubscribe(subid,False)
			print("CTRL-C pressed! Bye!")
			sys.exit(0)

