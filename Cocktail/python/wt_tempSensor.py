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
import logging
from wot_init import *
from webthing import *
from time import sleep

logging.basicConfig(format=LOGFORMAT,level=LOGLEVEL)

LEGGI_TEMPERATURA = "LeggiTemperatura"
NUOVA_TEMPERATURA = "NuovaTemperatura"

wt = WebThing(JSAP,JPAR,name="Termometro",uri="wot:Thermometer")
temperatura = Property(wt,"Temperatura",uri="wot:Temperatura",dataschema="float",writable=False,value="15.0")
leggi = Action(wt,name="LeggiTemperatura",uri="wot:LeggiTemperatura")
comunica = Event(wt,name="3sTemperatura",uri="wot:3sTemperatura",out_dataschema="float")

class ActionRequestHandler:
	def __init__(self):
		pass
	def handle(self, added, removed):
		for item in added:
			print(item)

def get_actual_value():
	# in questa funzione ci dovrebbe essere la comunicazione fisica con
	# il sensore per ricavare la temperatura
	return temperatura.value

if __name__ == '__main__':
	import sys
	
	wt.add_property(temperatura)
	wt.add_action(leggi)
	wt.add_event(comunica)
	wt.add_forProperty(leggi,temperatura)
	wt.add_forProperty(comunica,temperatura)
	
	wt.post()
	
	wt.listenForActionRequests(ActionRequestHandler())
	
	colorama.init()
	print(Fore.RED + "Waiting for action requests..." + Style.RESET_ALL)
	
	while True:
		try:
			sleep(5)
			comunica.throwNewEvent(output_value=get_actual_value())
		except KeyboardInterrupt:
			print("CTRL-C pressed! Bye!")
			sys.exit(0)
