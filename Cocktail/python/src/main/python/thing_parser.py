#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  thing_parser.py
#  
#  Copyright 2018 Francesco Antoniazzi <francesco.antoniazzi@unibo.it>
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

import json
from wot_init import *
from webthing import *

def jsonLD2Thing(jldFileString):
	data = json.loads(jldFileString)
	
	if not "td:Thing" in data["@type"]:
		return None
	wt = WebThing(name=data["name"],uri="wot{}".format(data["name"]))
	
	for item in data["interaction"]:
		if "td:Property" in item["@type"]:
			pr = Property(wt,item["name"],uri="wot{}".format(item["name"]),dataschema=item["dataschema"],writable=item["writable"],stability=item["stability"],value=item["start_value"])
			wt.add_property(pr)
			
	for item in data["interaction"]:
		obj = None
		
		in_ds = ""
		try:
			in_ds = item["input_dataschema"]
		except KeyError:
			pass
		
		out_ds = ""
		try:
			out_ds = item["output_dataschema"]
		except KeyError:
			pass
		
		if "td:Action" in item["@type"]:
			obj = Action(wt,name=item["name"],uri="wot{}".format(item["name"]),in_dataschema=in_ds,out_dataschema=out_ds)
			wt.add_action(obj)
		elif "td:Event" in item["@type"]:
			obj = Event(wt,name=item["name"],uri="wot{}".format(item["name"]),out_dataschema=out_ds)
			wt.add_event(obj)
		
		if not obj is None:
			try:
				for connection in item["connections"]:
					if connection["@type"]=="td:forProperty":
						print(type(obj))
						wt.add_forProperty(obj,wt.getProperty(connection["item"]))
			except KeyError:
				pass
	
	return wt
