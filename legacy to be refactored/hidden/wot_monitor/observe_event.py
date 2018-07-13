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

from cocktail.Event import Event

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
    
    observed = Event.buildFromQuery(sepa,"<"+args["Event-Instance-URI"]+">")
    print("Subscribing to event: \n{}".format(observed.bindings))
    if args["custom_handler"] is None:
        observed.observe(custom_handler)
    else:
        import importlib.util as iutil
        spec = iutil.spec_from_file_location("module.name",args["custom_handler"])
        module = iutil.module_from_spec(spec)
        spec.loader.exec_module(module)
        observed.observe(module.handler)
    try:
        while True:
            sleep(10)
    except KeyboardInterrupt:
        pass
    finally:
        observed.stop_observing()
        print("Bye Bye!")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="WoT Event subscriber")
    parser.add_argument("-ip", default="localhost", help="Sepa ip")
    parser.add_argument("-query_port", default=8000, help="Sepa query/update port")
    parser.add_argument("-sub_port", default=9000, help="Sepa subscription port")
    parser.add_argument("-token_uri", default=None, help="Sepa token uri")
    parser.add_argument("-registration_uri", default=None, help="Sepa registration uri")
    parser.add_argument("-custom_handler", default=None, help="Event handler location. The .py file must have a method inside called 'handler'")
    parser.add_argument("Event-Instance-URI",help="Uri of the event to which subscribe")
    arguments = vars(parser.parse_args())
    if ((arguments["token_uri"] is not None) and (arguments["registration_uri"] is not None)):
        arguments["security"] = True
    else:
        arguments["security"] = False
    sys.exit(main(arguments))
