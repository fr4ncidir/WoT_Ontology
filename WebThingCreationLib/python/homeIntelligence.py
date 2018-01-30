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

from webthing import *
from wot_init import *
import logging

logging.basicConfig(format="%(filename)s-%(funcName)s-%(levelname)s %(asctime)-15s %(message)s",level=logging.INFO)
logger = logging.getLogger("sepaLogger")

kp = LowLevelKP.LowLevelKP()

class HandlerTemperatura:
	def __init__(self):
		pass
	def handle(self, added, removed):
		for item in added:
			# Qui si implementa l'algoritmo di gestione della preferenza
			

def main(args):
	jsap_obj = JSAPObject.JSAPObject(JSAP)
	pref_jsap_obj = JSAPObject.JSAPObject("./homeIntelligence_jsap.jsap")
	# Before: get informations about the environment
	web_things = WebThing.discoveryThings(jsap_obj)
	actions = Action.getActionList(jsap_obj)
	properties = Property.getPropertyList(jsap_object)
	
	# First step: setup of preferences
	# le preferenze vengono fornite sotto forma di SPARQL filtrata. Per esempio
	# se voglio che la temperatura T sia T>20, filtrerò per valori <20
	# così se la query dà risultati so che la preferenza NON è al momento verificata.
	# Potrei anche sottoscrivermi, ed essere notificato quando essa passa da non verificata a verificata
	
	# NOTA: l'oggetto Preferenza si collega tramite 'isCorrectedBy' a tutti i dispositivi che lo possono
	# gestire. Verificare l'ordinabilità delle proprietà 'isCorrectedBy' tramite predicato-comesBefore-predicato

	logger.info("Subscribing to Temperature preference failure")
	sparql =  pref_jsap_obj.getQuery("FILTER_MINOR",{"property" : "wot:Temperatura", "boundary":"20.0"})
	subid = kp.subscribe(pref_jsap_obj.subscribeUri,sparql, "Pref_temperatura", HandlerTemperatura())

	# Fourth step: identification of the device and the action
	
	
	return 0

if __name__ == '__main__':
	import sys
	sys.exit(main(sys.argv))
