#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  senza nome.py
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

from shutil import copy
import xml.etree.ElementTree as ET
import json

TD_template = "./thing_description.jsap"
TD_complete = "./thing_description2.jsap"
ontology_namespace = "http://wot.arces.unibo.it/ontology/web_of_things#"
namespaces = {"owl","http://www.w3.org/2002/07/owl#"}

def main(args):
	copy(TD_template,TD_complete)
	
	owl = ET.parse("./td.owl")
	root = owl.getroot()
	for element in root.findall("{http://www.w3.org/2002/07/owl#}AnnotationProperty"):
		for item in element.attrib.values():
			print("-->{}".format(item))
	
	with open(TD_complete,"r+") as jsap:
		data = json.load(jsap)
		data["queries"]["francesco"]="ciao"
		data["queries"]["wilbur"]="smith"
		jsap.seek(0)
		json.dump(data,jsap,indent=4)
		jsap.truncate()
	return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
