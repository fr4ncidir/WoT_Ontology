#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  new_thing.py
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
#  This thing is equivalent to the one in insert_thing_1.sparql
#     _____ _     _             _
#    |_   _| |__ (_)_ __   __ _/ |
#      | | | '_ \| | '_ \ / _` | |
#      | | | | | | | | | | (_| | |
#      |_| |_| |_|_|_| |_|\__, |_|
#                         |___/
import sys
sys.path.append("C:/Users/Francesco/Documents/Work/WoT_Ontology")

from wrap_sepa import Sepa as Engine
from time import sleep
from datetime import datetime
from cocktail.Thing import Thing
from cocktail.DataSchema import DataSchema
from cocktail.Property import Property
from cocktail.Action import Action
from cocktail.Event import Event

import sparql_utilities as bzu
import constants as cst

xsd_string = "xsd:string"
xsd_integer = "xsd:integer"
xsd_dateTimeStamp = "xsd:dateTimeStamp"
xsd_ = "xsd:_"
wot_FieldSchema = "wot:FieldSchema"
thing_descriptor = "<http://MyFirstWebThingDescription.com>"

def main(args):
    graph = Engine()
    
    answer = input("Clear the RDF store? (y/n)")
    if answer.lower() == "y":
        print("Clearing the RDF store...")
        graph.update("delete where {?a ?b ?c}")
    else:
        print("I'm not clearing the RDF store...")
    
    print("Posting DataSchemas...")
    ds1 = DataSchema(graph, { "ds_uri": "<http://MyFirstWebThing.com/Action1/DataSchema/input>",
                        "fs_uri": xsd_string,
                        "fs_types": xsd_+", "+wot_FieldSchema}).post()
    ds2 = DataSchema(graph, { "ds_uri": "<http://MyFirstWebThing.com/Action1/DataSchema/output>",
                        "fs_uri": "<http://www.wikipedia.it>",
                        "fs_types": "wot:ResourceURI, "+wot_FieldSchema}).post()
    ds3 = DataSchema(graph, { "ds_uri": "<http://MyFirstWebThing.com/Action2/DataSchema/output>",
                        "fs_uri": xsd_integer,
                        "fs_types": xsd_+", "+wot_FieldSchema}).post()
    ds4 = DataSchema(graph, { "ds_uri": "<http://MyFirstWebThing.com/Event1/DataSchema/output>",
                        "fs_uri": xsd_dateTimeStamp,
                        "fs_types": xsd_+", "+wot_FieldSchema}).post()
    ds5 = DataSchema(graph, { "ds_uri": "<http://MyFirstWebThing.com/Property1/DataSchema/property>",
                        "fs_uri": xsd_string,
                        "fs_types": xsd_+", "+wot_FieldSchema}).post()
    print("Dataschemas posted!")
                    
    thing1 = Thing(graph,{  "thing": "<http://MyFirstWebThing.com>",
                            "newName": "Thing1",
                            "newTD": thing_descriptor }).post()
    print("Thing added!")
                            
    property1 = Property(graph,{ "td": thing_descriptor,
                    "property": "<http://MyFirstWebThing.com/Property1>",
                    "newName": "Thing1_Property1",
                    "newStability": "1000",
                    "newWritability": "true",
                    "newDS": ds5.uri,
                    "newPD": "<http://MyFirstWebThing.com/Property1/PropertyData>",
                    "newValue": "Hello World!"}).post()
    print("Property added to thing!")
                    
    action1 = Action(graph,{"thing": thing1.uri,
                            "td": thing_descriptor,
                            "action": "<http://MyFirstWebThing.com/Action1>",
                            "newName": "Thing1_Action1",
                            "ids": ds1.uri,
                            "ods": ds2.uri},
                            lambda: print("ACTION 1 HANDLER RUN")).post().enable()
    print("Action1 added to thing!")
    
    action2 = Action(graph,{"thing": thing1.uri,
                            "td": thing_descriptor,
                            "action": "<http://MyFirstWebThing.com/Action2>",
                            "newName": "Thing1_Action2",
                            "ods": ds3.uri},
                            lambda: print("ACTION 2 HANDLER RUN"),
                            forProperties=[property1]).post().enable()
    print("Action2added to thing!")
                            
    event1 = Event(graph,{  "td": thing_descriptor,
                            "event": "<http://MyFirstWebThing.com/Event1>",
                            "eName": "Thing1_Event1",
                            "ods": ds4.uri}).post()
    print("Event added to thing!")
          
    
    graph.query("select * where {?a ?b ?c}",destination="./missing.txt")
    graph.update("delete where {?a ?b ?c}")
    graph.update(bzu.file_to_string(cst.SPARQL_INSERT_THING1))
    graph.query("select * where {?a ?b ?c}",destination="./res_thing1.txt")
    bzu.compare_queries("./missing.txt","./res_thing1.txt",show_diff=True)
    
    # input("Continue?")
    
    # print("Now I'll trigger 10 events, one every 10 seconds. ")
    # for trigger_event1 in range(10):
        # print("... Firing event {}".format(trigger_event1))
        # instance = event1.notify({ "event": event1.uri,
                        # "newEInstance": event1.uri.replace(">","/instance{}>".format(trigger_event1)),
                        # "newOData": event1.uri.replace(">","/data{}>".format(trigger_event1)),
                        # "newValue": str(datetime.utcnow()).replace(" ","T")+"Z",
                        # "newDS": ds4.uri})
        # sleep(10)
        # print("Deleting old event instance...")
        # event1.deleteInstance(instance)
    # print("Stopping triggering events!")
    
    # print("Now I'll disable the two actions.")
    # action1.disable()
    # action2.disable()
    # print("Actions disabled!")
    
    # print("Now I'll remove the thing.")
    # thing1.delete()
    # print("Thing deleted! Only DataSchemas should be remaining in the RDF store.")
    
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
