#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  ontology_test_suite.py
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

import unittest
import logging
import requests
import argparse
import xml.etree.ElementTree as etree
import yaml
import json
import copy
import blazegraph as bz

logging.basicConfig(format='%(levelname)s %(asctime)-15s %(message)s',level=logging.INFO)

class TestOntologySPARQL(unittest.TestCase):
    def setUp(self):
        # Check Blazegraph is online, delete all, insert test dummy data
        r = bz.update_blazegraph(args,"DELETE WHERE {?a ?b ?c}")
        self.assertEqual(r.status_code,200,r)
    
    def test_1_Blazegraph(self):
        # Check Blazegraph is online
        r = query_blazegraph(args,"SELECT * WHERE {?a ?b ?c} LIMIT 1")
        self.assertEqual(r.status_code,200,r)
    
    def test_2_delete_all(self):
        r = update_blazegraph(args,"DELETE WHERE {?a ?b ?c}")
        self.assertEqual(r.status_code,200,r)
    
    def test_3_insert_things(self):
        print("")
        r = update_blazegraph(args,file_to_string("./insert_thing_1.sparql"))
        self.assertEqual(r.status_code,200,r)
        logging.info("Successful INSERT DATA for Thing1")
        r = update_blazegraph(args,file_to_string("./insert_thing_2.sparql"))
        self.assertEqual(r.status_code,200,r)
        logging.info("Successful INSERT DATA for Thing2")
        
    def test_4_parse_ontology(self):
        print("")
        tree = etree.parse(args["owl"])
        root = tree.getroot()
        ontology = root.find("owl:Ontology",ns)
        for annotation_property in root.findall("owl:AnnotationProperty",ns):
            annotation = annotation_property.attrib["{}about".format("{"+ns["rdf"]+"}")].replace(ns["wot"],"wot:")
            for annotation_type in annotation_property.findall("rdfs:subPropertyOf",ns):
                annotation_type_string = annotation_type.attrib["{}resource".format("{"+ns["rdf"]+"}")]
                for ysap_entry in root.findall(".//"+annotation,ns):
                    yaml_object = yaml.load(ysap_entry.text)
                    yaml_object_root = yaml.dump(yaml_object)
                    if annotation_type_string == ns["wot"]+"query":
                        queries[annotation.replace("wot:","")] = yaml_object
                        logging.info("Loaded query {}".format(yaml_object_root[:yaml_object_root.index(":")]))
                    elif annotation_type_string == ns["wot"]+"update":
                        updates[annotation.replace("wot:","")] = yaml_object
                        logging.info("Loaded update {}".format(yaml_object_root[:yaml_object_root.index(":")]))
                    elif annotation_type_string == ns["wot"]+"delete":
                        deletes[annotation.replace("wot:","")] = yaml_object
                        logging.info("Loaded delete {}".format(yaml_object_root[:yaml_object_root.index(":")]))
                    else:
                        logging.warning("Unknown annotation: {}".format(annotation_type_string))
    
    def test_5_discover_things(self):
        print("")
        sparql,fB = get_yaml_data("thing",queries)
        r = query_blazegraph(args,sparql,forcedbindings=fB)
        self.assertEqual(r.status_code,200,r)
        self.assertTrue(json_equal(r.text,"./test_results/test5_result.json"))
        
    def test_6_thing_description(self):
        print("")
        sparql,_ = get_yaml_data("thing_description",queries)
        r = query_blazegraph(args,sparql)
        self.assertEqual(r.status_code,200,r)
        #print(r.text, file=open("./test_results/test6_result.json","w"))
        self.assertTrue(json_equal(r.text,"./test_results/test6_result.json"))
        
    def test_7_interaction_patterns(self):
        print("")
        for index,item in enumerate(["interaction_pattern","action","event","property"]):
            logging.info("Performing {} query".format(item))
            sparql,fB = get_yaml_data(item,queries)
            r = query_blazegraph(args,sparql,forcedbindings=fB)
            self.assertEqual(r.status_code,200,r)
            #print(r.text, file=open("./test_results/test7_result{}.json".format(index+1),"w"))
            self.assertTrue(json_equal(r.text,"./test_results/test7_result{}.json".format(index+1)))
    
    def test_8_dataschema(self):
        print("")
        sparql,fB = get_yaml_data("data_field_schema",queries)
        r = query_blazegraph(args,sparql,forcedbindings=fB)
        self.assertEqual(r.status_code,200,r)
        #print(r.text, file=open("./test_results/test8_result.json","w"))
        self.assertTrue(json_equal(r.text,"./test_results/test8_result.json"))
        
    def test_9_dataschema(self):
        # add input dataschema 1
        
        # add output dataschema 2
        
        # query check
        
        # delete dataschema 1
        
        # query check
        
        # add again dataschema 1
        
    def test_10_new_thing(self):
        print("")
        SUPERTHING = "<http://MyFirstWebThing.com>"
        NEW_THING = "<http://thing_three.com>"
        NEW_THING_NAME = "Thing3"
        NEW_THING_TD = "<http://td_three.com>"
        # add thing
        sparql,_ = get_yaml_data("new_thing",updates)
        fB = {"thing": NEW_THING,
            "newName": NEW_THING_NAME,
            "newTD": NEW_THING_TD}
        self.assertEqual(update_blazegraph(args,sparql,fB).status_code,200)
        logging.info("Successfully added new thing")
        # append as subthing
        sparql,_ = get_yaml_data("new_subthing",updates)
        fB = {"superthing": SUPERTHING,
            "subthing": NEW_THING}
        self.assertEqual(update_blazegraph(args,sparql,fB).status_code,200)
        logging.info("Successfully appended thing as subthing")
        # add i action
        I_ACTION_URI = NEW_THING.replace(">","/IAction>")
        I_ACTION_NAME = "iAction"
        sparql,_ = get_yaml_data("new_i_action",updates)
        fB = {"action": I_ACTION_URI,
            "newName": I_ACTION_NAME,
            "newDSs": I_DATASCHEMA,
            "newIDS": I_DATASCHEMA}
        self.assertEqual(update_blazegraph(args,sparql,fB).status_code,200)
        logging.info("Successfully added input action")
        # add o action
        O_ACTION_URI = NEW_THING.replace(">","/OAction>")
        O_ACTION_NAME = "oAction"
        O_ACTION_DS = NEW_THING.replace(">","/OAction/DataSchema/output>")
        sparql,_ = get_yaml_data("new_o_action",updates)
        fB = {"action": I_ACTION_URI,
            "newName": I_ACTION_NAME,
            "newDSs": O_DATASCHEMA,
            "newODS": O_DATASCHEMA}
        self.assertEqual(update_blazegraph(args,sparql,fB).status_code,200)
        logging.info("Successfully added output action")
        # add io action
        IO_ACTION_URI = NEW_THING.replace(">","/IOAction>")
        IO_ACTION_NAME = "ioAction"
        IO_ACTION_IDS = NEW_THING.replace(">","/IOAction/DataSchema/input>")
        IO_ACTION_ODS = NEW_THING.replace(">","/IOAction/DataSchema/output>")
        sparql,_ = get_yaml_data("new_io_action",updates)
        fB = {"action": IO_ACTION_URI,
            "newName": IO_ACTION_NAME,
            "newDSs": "{}, {}".format(IO_ACTION_IDS,IO_ACTION_ODS),
            "newIDS": IO_ACTION_IDS,
            "newODS": IO_ACTION_ODS}
        self.assertEqual(update_blazegraph(args,sparql,fB).status_code,200)
        logging.info("Successfully added input-output action")
        # add empty action
        EMPTY_ACTION_URI = NEW_THING.replace(">","/EMPTYAction>")
        EMPTY_ACTION_NAME = "emptyAction"
        sparql,_ = get_yaml_data("new_empty_action",updates)
        fB = {"action": EMPTY_ACTION_URI,
            "newName": EMPTY_ACTION_NAME}
        self.assertEqual(update_blazegraph(args,sparql,fB).status_code,200)
        logging.info("Successfully added empty action")
        # add o event
        O_EVENT_URI = NEW_THING.replace(">","/OEvent>")
        O_EVENT_NAME = "oEvent"
        O_EVENT_DS = NEW_THING.replace(">","/OEvent/DataSchema/output>")
        sparql,_ = get_yaml_data("new_o_event",updates)
        fB = {"event": O_EVENT_URI,
            "newName": O_EVENT_NAME,
            "newDSs": O_EVENT_DS,
            "newODS": O_EVENT_DS}
        self.assertEqual(update_blazegraph(args,sparql,fB).status_code,200)
        logging.info("Successfully added output event")
        # add empty event
        EMPTY_EVENT_URI = NEW_THING.replace(">","/EMPTYEvent>")
        EMPTY_EVENT_NAME = "emptyEvent"
        sparql,_ = get_yaml_data("new_empty_event",updates)
        fB = {"event": EMPTY_EVENT_URI,
            "newName": EMPTY_EVENT_NAME}
        self.assertEqual(update_blazegraph(args,sparql,fB).status_code,200)
        logging.info("Successfully added output event")
        # add property
        # PROPERTY_URI = NEW_THING.replace(">","/Property>")
        # PROPERTY_NAME = "newProperty"
        # PROPERTY_STABILITY = "95"
        # PROPERTY_WRITABILITY = "true"
        # PROPERTY_DS = 
        # sparql,_ = get_yaml_data("new_property",updates)
        # append items to thing descriptor
        # check with queries
        # delete
        # check again
        
def main():
    unittest.main(verbosity=2,failfast=True)
    return 0

if __name__ == '__main__':
    import sys
    parser = argparse.ArgumentParser(description="WoT ontology test suite")
    parser.add_argument("-ip", default="localhost", help="Blazegraph ip")
    parser.add_argument("-port", default=9999, help="Blazegraph port")
    parser.add_argument("-owl", default="../ontologia.owl", help="Path to ontology")
    args = vars(parser.parse_args())
    sys.exit(main())
