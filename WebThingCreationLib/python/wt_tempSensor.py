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

import logging
from wot_init import *
from webthing import *

logging.basicConfig(format="%(levelname)s %(asctime)-15s %(message)s",level=LOGLEVEL)

LEGGI_TEMPERATURA = "LeggiTemperatura"
NUOVA_TEMPERATURA = "NuovaTemperatura"

wt = WebThing(JSAP,JPAR,name="Termometro",uri="wot:Thermometer")
temperatura = Property(wt,"Temperatura",uri="wot:Temperatura",dataschema="float",writable=False,value="15")
leggi = Action(wt,name="LeggiTemperatura",uri="wot:LeggiTemperatura")
comunica = Event(wt,name="3sTemperatura",uri="wot:3sTemperatura",out_dataschema="float")

class ActionRequestHandler:
	def __init__(self):
		pass
	def handle(self, added, removed):
		print("Added: {}",added)
		print("Removed: {}",removed)
		for item in added:
			if item["action"]["value"]=="{}{}".format(WOT,ACCENDI_RISCALDAMENTO):
				print("Riscaldamento acceso alle {}".format(item["request"]["value"]))
				accendi.postActionConfirmation(item["instance"]["value"])
				accendi.postActionCompletion(item["instance"]["value"])
			elif item["action"]["value"]=="{}{}".format(WOT,SPEGNI_RISCALDAMENTO):
				print("Riscaldamento spento alle {}".format(item["request"]["value"]))
				spegni.postActionConfirmation(item["instance"]["value"])
				spegni.postActionCompletion(item["instance"]["value"])

if __name__ == '__main__':
	import sys
	
	wt.add_property(temperatura)
	wt.add_action(leggi)
	wt.add_event(comunica)
	wt.add_forProperty(leggi,temperatura)
	wt.add_forProperty(comunica,temperatura)
	
	wt.post()
	
	wt.listenForActionRequests(ActionRequestHandler())
	
	print("Waiting for action requests...")
		
	while True:
		try:
			pass
		except KeyboardInterrupt:
			print("CTRL-C pressed! Bye!")
			sys.exit(0)
