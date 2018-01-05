#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  wt_heater.py
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

logging.basicConfig(format="%(levelname)s %(asctime)-15s %(message)s",level=LOGLEVEL)

ACCENDI_RISCALDAMENTO = "AccendiRiscaldamento"
SPEGNI_RISCALDAMENTO = "SpegniRiscaldamento"

wt = WebThing(JSAP,JPAR,name="Riscaldamento",uri="wot:Heater")
consumo = Property(wt,"Consumo",uri="wot:Consumo",dataschema="float",writable=False,value="0")
accendi = Action(wt,name="AccendiRiscaldamento",uri="wot:AccendiRiscaldamento")
spegni = Action(wt,name="SpegniRiscaldamento",uri="wot:SpegniRiscaldamento")

class ActionRequestHandler:
	def __init__(self):
		pass
	def handle(self, added, removed):
		for item in added:
			if item["action"]["value"]=="{}{}".format(WOT,ACCENDI_RISCALDAMENTO):
				print("Riscaldamento acceso alle {}".format(item["request"]["value"]))
				accendi.postActionConfirmation(item["instance"]["value"])
				logger.info("Updating property {} value to {}".format(consumo.getName(),"50"))
				sparql = wt.getKP().jsapHandler.getUpdate("UPDATE PROPERTY VALUE",{"property" : consumo.getUri(), "newValue" : "50"})
				wt.getKP().update(sparql,secure)
				accendi.postActionCompletion(item["instance"]["value"])
			elif item["action"]["value"]=="{}{}".format(WOT,SPEGNI_RISCALDAMENTO):
				print("Riscaldamento spento alle {}".format(item["request"]["value"]))
				spegni.postActionConfirmation(item["instance"]["value"])
				logger.info("Updating property {} value to {}".format(consumo.getName(),"0"))
				sparql = wt.getKP().jsapHandler.getUpdate("UPDATE PROPERTY VALUE",{"property" : consumo.getUri(), "newValue" : "0"})
				wt.getKP().update(sparql,secure)
				spegni.postActionCompletion(item["instance"]["value"])

if __name__ == '__main__':
	import sys
	
	wt.add_property(consumo)
	wt.add_action(accendi)
	wt.add_action(spegni)
	wt.add_forProperty(accendi,consumo)
	wt.add_forProperty(spegni,consumo)
	
	wt.post()
	
	wt.listenForActionRequests(ActionRequestHandler())
	
	colorama.init()
	print(Fore.RED + "Waiting for action requests..." + Style.RESET_ALL)
		
	while True:
		try:
			pass
		except KeyboardInterrupt:
			print("CTRL-C pressed! Bye!")
			sys.exit(0)
