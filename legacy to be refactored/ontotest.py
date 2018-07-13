#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  prove.py
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

from sepy.Sepa import Sepa as Engine
#from blazegraph import Blazegraph as Engine
import yaml
import json
import sepy.utils as utils
import wot_test as test
import argparse
import logging
import cocktail.constants as cst

logger = logging.getLogger("ontology_test_log") 
logging.basicConfig(format='%(levelname)s %(asctime)-15s %(message)s',level=logging.INFO) 

def main(args):
    logger.setLevel(logging.INFO)
    if args["reset"]:
        confirm = input("Detected reset request! Are you sure? (y/n) ")
        if not confirm.lower()=="y":
            print("Abort")
            return 1

    myBZ = Engine(ip=args["ip"])
    test.reset_testbase(myBZ)
    
    if args["reset"]:
        result = myBZ.query(cst.SPARQL_QUERY_ALL,destination=cst.RES_SPARQL_QUERY_ALL)
        logging.warning("Rebuilding {} ({} bindings)".format(cst.RES_SPARQL_QUERY_ALL,len(result["results"]["bindings"])))
    else:
        # 1st check: after the updates the content of the store has to be the same as in the json
        # this call exploits default params.
        result = utils.query_FileCompare(myBZ,fileAddress=cst.RES_SPARQL_QUERY_ALL)
    
    # 2nd check: every query in ./queries folder
    result = result and test.test_queries(myBZ,args["reset"])
    
    # 3rd check: adding and removing a thing
    result = result and utils.notify_result("test_thing",test.test_new_thing(myBZ,reset=args["reset"]))
    
    # 4th check: adding and removing a property
    result = result and utils.notify_result("test_new_property",test.test_new_property(myBZ,reset=args["reset"]))
    
    # 5th check: adding and removing actions
    result = result and utils.notify_result("test_new_actions",test.test_new_action(myBZ,reset=args["reset"]))
    
    # 6th check: adding and removing events
    result = result and utils.notify_result("test_new_events",test.test_new_event(myBZ,reset=args["reset"]))
    
    # 7th check: action instance
    result = result and utils.notify_result("test_new_events",test.test_action_instance(myBZ,reset=args["reset"]))
    
    # 8th check: action instance
    result = result and utils.notify_result("test_new_events",test.test_event_instance(myBZ,reset=args["reset"]))
    
    utils.notify_result("Ontology test result",result)
    
    return 0

if __name__ == '__main__':
    import sys
    parser = argparse.ArgumentParser(description="Web Of Things ontology check")
    parser.add_argument("-ip", default="localhost", help="Blazegraph ip")
    parser.add_argument("-port", default=8888, help="Blazegraph port")
    parser.add_argument("--reset", action="store_true", help="Rebuild json outputs")
    sys.exit(main(vars(parser.parse_args())))
