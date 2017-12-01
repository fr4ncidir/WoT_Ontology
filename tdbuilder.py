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
import xml.etree.ElementTree as etree
import json
import sys
import datetime

TD_template = "./thing_description.jsap"
TD_complete = "./thing_description2.jsap"
sepa_annotations = "http://www.semanticweb.org/francesco/ontologies/2017/9/sepa_annotations#"

ns = {	"owl"			:"http://www.w3.org/2002/07/owl#",
		"web_of_things"	:"http://wot.arces.unibo.it/ontology/web_of_things#",
		"rdf"			:"http://www.w3.org/1999/02/22-rdf-syntax-ns#",
		"rdfs"			:"http://www.w3.org/2000/01/rdf-schema#"}
		
def jsap_build(entry,jsap_level,json_data,jsap_file):
	entry_data = entry.replace("\n","").split(":",1)
	j_key = entry_data[0][1:-1]
	try:
		j_object = json.loads(entry_data[1])
	except:
		print("Error while parsing {}\n{}:\n{}".format(entry,j_key,sys.exc_info()[1]))
		sys.exit(1)
	json_data[jsap_level][j_key]=j_object
	jsap_file.seek(0)
	json.dump(json_data,jsap_file,indent=4)
	jsap_file.truncate()

def main(args):
	copy(TD_template,TD_complete)
	
	tree = etree.parse("./td.owl")
	root = tree.getroot()
	queries = []
	updates = []
	for element in root.findall("owl:AnnotationProperty",ns):
		for annotation_type in element.findall("rdfs:subPropertyOf",ns):
			#print("{} {}".format(annotation_type.tag,annotation_type.attrib))
			annotation_type_string = annotation_type.attrib["{}{}".format("{"+ns["rdf"]+"}","resource")]
			#print(annotation_type_string)
			if (annotation_type_string==(ns["web_of_things"]+"discovery")) or (annotation_type_string==(ns["web_of_things"]+"query")):
				queries.append(element.attrib["{}{}".format("{"+ns["rdf"]+"}","about")].replace(ns["web_of_things"],"web_of_things:"))
			elif (annotation_type_string==(ns["web_of_things"]+"delete")) or (annotation_type_string==(ns["web_of_things"]+"update")):
				updates.append(element.attrib["{}{}".format("{"+ns["rdf"]+"}","about")].replace(ns["web_of_things"],"web_of_things:"))
	
	with open(TD_complete,"r+") as jsap:
		data = json.load(jsap)
		data["creation_time"]="{:%Y-%m-%d %H:%M:%S}".format(datetime.datetime.now())
		for element in queries:
			for item in root.findall(".//"+element,ns):
				jsap_build(item.text,"queries",data,jsap)
		for element in updates:
			for item in root.findall(".//"+element,ns):
				jsap_build(item.text,"updates",data,jsap)
	return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
