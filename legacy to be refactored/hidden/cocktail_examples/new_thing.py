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
sys.path.append("/home/tarsier/Documents/Work/WoT_Ontology")

from sepy.Sepa import Sepa as Engine
import sepy.utils as utils
from time import sleep
from datetime import datetime
from cocktail.Thing import Thing
from cocktail.DataSchema import DataSchema
from cocktail.Property import Property
from cocktail.Action import Action
from cocktail.Event import Event

import threading
import argparse
import logging

logger = logging.getLogger("cocktail_log") 

xsd_string = "xsd:string"
xsd_integer = "xsd:integer"
xsd_dateTimeStamp = "xsd:dateTimeStamp"
xsd_ = "xsd:_"
wot_FieldSchema = "wot:FieldSchema"
thing_descriptor = "<http://MyFirstWebThingDescription.com>"

def main(args):
    action1 = None
    action1Lock = threading.Lock()
    
    graph = Engine(  ip = args["ip"],
                    http_port = args["query_port"],
                    ws_port = args["sub_port"],
                    security =     {"secure": args["security"], 
                                    "tokenURI": args["token_uri"], 
                                    "registerURI": args["registration_uri"]})
    
    if args["clear"]:
        print("Clearing the RDF store...")
        graph.update("delete where {?a ?b ?c}")
    
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
    
    def action1Handler(added,removed):
        action1Lock.acquire()
        if len(added)>0:
            print("\n*******ACTION 1 HANDLER START**********")
            print("Added: {}\nRemoved: {}".format(added,removed))
            print("*******ACTION 1 HANDLER END**********\n")
            for instance in added:
                action1.post_confirmation(utils.uriFormat(instance["aInstance"]["value"]))
                action1.post_output({   "instance": utils.uriFormat(instance["aInstance"]["value"]),
                                        "oData": utils.uriFormat("http://ODATA_"+str(datetime.now()).replace(" ","T").replace(":","_")+"Z"),
                                        "oValue": instance["iValue"]["value"][::-1],
                                        "oDS": action1.bindings["ods"]})
        action1Lock.release()
        
    action1 = Action(graph,{"thing": thing1.uri,
                            "td": thing_descriptor,
                            "action": "<http://MyFirstWebThing.com/Action1>",
                            "newName": "Thing1_Action1",
                            "ids": ds1.uri,
                            "ods": ds2.uri},
                            action1Handler).post().enable()
    print("Action1 added to thing!")
    
    action2 = Action(graph,{"thing": thing1.uri,
                            "td": thing_descriptor,
                            "action": "<http://MyFirstWebThing.com/Action2>",
                            "newName": "Thing1_Action2",
                            "ods": ds3.uri},
                            lambda a,r: print("ACTION 2 HANDLER RUN"),
                            forProperties=[property1]).post().enable()
    print("Action2added to thing!")
                            
    event1 = Event(graph,{  "td": thing_descriptor,
                            "event": "<http://MyFirstWebThing.com/Event1>",
                            "eName": "Thing1_Event1",
                            "ods": ds4.uri}).post()
    print("Event added to thing!")
    
    #input("Continue?")
    
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
    
    #input("Continue?")
    
    try:
        while True:
            sleep(10)
    except KeyboardInterrupt:
        print("Bye Bye!")
    
    # print("Now I'll disable the two actions.")
    # action1.disable()
    # action2.disable()
    # print("Actions disabled!")
    
    # print("Now I'll remove the thing.")
    # thing1.delete()
    # print("Thing deleted! Only DataSchemas should be remaining in the RDF store.")
    
    return 0

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="New Thing example script")
    parser.add_argument("-ip", default="localhost", help="Sepa ip")
    parser.add_argument("-query_port", default=8000, help="Sepa query/update port")
    parser.add_argument("-sub_port", default=9000, help="Sepa subscription port")
    parser.add_argument("-token_uri", default=None, help="Sepa token uri")
    parser.add_argument("-registration_uri", default=None, help="Sepa registration uri")
    parser.add_argument("-clear",action="store_true",help="Clears the SEPA before anything else")
    arguments = vars(parser.parse_args())
    if ((arguments["token_uri"] is not None) and (arguments["registration_uri"] is not None)):
        arguments["security"] = True
    else:
        arguments["security"] = False
    sys.exit(main(arguments))
