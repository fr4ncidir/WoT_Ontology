#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  observe_event.py
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

import sys
sys.path.append("/home/tarsier/Documents/Work/WoT_Ontology")

from sepy.Sepa import Sepa as Engine
from sepy import utils

from cocktail.Action import *
from cocktail.DataSchema import DataSchema

from datetime import datetime
from time import sleep
import argparse

def custom_handler(added,removed):
    print("\n**************************************************************")
    print("ADDED: {}".format(added))
    print("REMOVED: {}".format(removed))
    print("**************************************************************\n")

def main(args):
    sepa = Engine(  ip = args["ip"],
                    http_port = args["query_port"],
                    ws_port = args["sub_port"],
                    security =     {"secure": args["security"], 
                                    "tokenURI": args["token_uri"], 
                                    "registerURI": args["registration_uri"]})
    
    action = Action.buildFromQuery(sepa,utils.uriFormat(args["Action-URI"]))
    if args["custom_handler"] is None:
        if ((action.type is AType.IO_ACTION) or (action.type is AType.OUTPUT_ACTION)):
            def handler(a,r):
                print("\n**************************************")
                print("Request action output handler! ")
                print("Added: {}".format(a))
                print("Removed: {}".format(r))
                print("**************************************\n")
        else:
            handler = None
    else:
        import importlib.util as iutil
        spec = iutil.spec_from_file_location("module.name",args["custom_handler"])
        module = iutil.module_from_spec(spec)
        spec.loader.exec_module(module)
        handler = module.handler
    
    bindings = {"action": action.uri,
                "newAInstance": "AInstance_"+str(datetime.now()).replace(" ","T")+"Z",
                "newAuthor": "MonitorPython"}
    if ((action.type is AType.IO_ACTION) or (action.type is AType.INPUT_ACTION)):
        print("Please give input according to the following dataschema: ")
        print("DS info:")
        dss = DataSchema.discover(sepa,ds=action.bindings["ids"],nice_output=True)["results"]["bindings"]
        
        if len(dss)>1:
            chosen_format = {}
            for ds in dss:
                queried_format[ds["ds"]["value"]] = ds["fs"]["value"]
            bindings["newIDS"] = input(">> Please insert the DataSchema Uri chosen: ")
            chosen_format = queried_format[chosen_ds]
        else:
            bindings["newIDS"] = dss[0]["ds"]["value"]
            chosen_format = dss[0]["fs"]["value"]
        bindings["newIValue"] = input("({}) Insert input in {} format > ".format(bindings["newIDS"],chosen_format))
        bindings["newIData"] = "IDATA_"+str(datetime.now()).replace(" ","T")+"Z"
        
    action.newRequest(  bindings,
                        confirm_handler=lambda a,r: print("\nConfirmation handler:\na: {}\nr: {}".format(a,r)),
                        completion_handler=lambda a,r: print("\nCompletion handler:\na: {}\nr: {}".format(a,r)),
                        output_handler=handler)
    try:
        while True:
            sleep(10)
    except KeyboardInterrupt:
        pass
    finally:
        print("Bye Bye!")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="WoT Action requestor")
    parser.add_argument("-ip", default="localhost", help="Sepa ip")
    parser.add_argument("-query_port", default=8000, help="Sepa query/update port")
    parser.add_argument("-sub_port", default=9000, help="Sepa subscription port")
    parser.add_argument("-token_uri", default=None, help="Sepa token uri")
    parser.add_argument("-registration_uri", default=None, help="Sepa registration uri")
    parser.add_argument("-custom_handler", default=None, help="Action output handler location. The .py file must have a method inside called 'handler'")
    parser.add_argument("Action-URI",help="Uri of the action to be requested")
    arguments = vars(parser.parse_args())
    if ((arguments["token_uri"] is not None) and (arguments["registration_uri"] is not None)):
        arguments["security"] = True
    else:
        arguments["security"] = False
    sys.exit(main(arguments))
