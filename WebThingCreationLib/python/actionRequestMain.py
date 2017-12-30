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

from webthing import *
from wot_init import *

logging.basicConfig(format="%(levelname)s %(asctime)-15s %(message)s",level=LOGLEVEL)

class ConfirmationHandler:
	def __init__(self):
		pass
	def handle(self, added, removed):
		for item in added:
			logging.info("Action Confirmation handler: {} timestamp received".format(item["timestamp"]["value"]))

def main(args):
	instance = Action.askForAction(JPAR,JSAP,"wot:Heater","wot:AccendiRiscaldamento")
	Action.waitActionConfirmation(JPAR,JSAP,instance,ConfirmationHandler())

if __name__ == '__main__':
	import sys
	main(sys.argv)
	while True:
		try:
			pass
		except KeyboardInterrupt:
			print("CTRL-C pressed! Bye!")
			sys.exit(0)

