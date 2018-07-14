#!/usr/bin python3
# -*- coding: utf-8 -*-
#
#  TestCase2_Subscriptions.py
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

from cocktail.constants import SPARQL_INSERT_THING1, SPARQL_INSERT_THING2, SPARQL_INSERT_THING3
from cocktail.constants import SPARQL_PREFIXES as WotPrefs
from cocktail.constants import PATH_SPARQL_QUERY_PROPERTY as queryProperty
from cocktail.constants import PATH_SPARQL_QUERY_TS_TEMPLATE, RES_SPARQL_NEW_TS_TEMPLATE
from cocktail.constants import PATH_SPARQL_QUERY_THING, RES_SPARQL_NEW_THING
from cocktail.constants import RES_SPARQL_QUERY_ALL
from cocktail.constants import RES_SPARQL_QUERY_ALL_NEW_DATASCHEMA
from cocktail.constants import RES_SPARQL_NEW_PROPERTY, RES_SPARQL_NEW_PROPERTY_UPDATE
from cocktail.constants import RES_SPARQL_QUERY_ALL_NEW_DS_ACTIONS, RES_SPARQL_QUERY_ALL_NEW_DS_EVENTS
from cocktail.constants import PATH_SPARQL_QUERY_ACTION, RES_SPARQL_NEW_ACTIONS
from cocktail.constants import PATH_SPARQL_QUERY_EVENT, RES_SPARQL_NEW_EVENTS
from cocktail.constants import PATH_SPARQL_QUERY_ACTION_INSTANCE, RES_SPARQL_NEW_ACTION_INSTANCE_TEMPLATE
from cocktail.constants import PATH_SPARQL_QUERY_INSTANCE_OUTPUT, RES_SPARQL_NEW_INSTANCE_OUTPUT
from cocktail.constants import RES_SPARQL_NEW_ACTION_INSTANCE_UPDATE_TEMPLATE, RES_SPARQL_NEW_EVENT_INSTANCE_TEMPLATE
from cocktail.constants import PATH_SPARQL_QUERY_EVENT_INSTANCE
from cocktail.constants import RES_SPARQL_NEW_EVENT_INSTANCE_UPDATE_TEMPLATE

from cocktail.Thing import Thing
from cocktail.DataSchema import DataSchema
from cocktail.Property import Property
from cocktail.Action import *
from cocktail.Event import *

import sepy.utils as utils
from sepy.Sepa import Sepa as Engine
from sepy.YSparqlObject import ysparql_to_string as y2str

from .TestCase2_QueryUpdate import reset_testbase

def add_action_instance_ts(graph,instance,action):
    for c in ["confirmation","completion"]:
        action._post_timestamp(c,instance)
        if not utils.query_CompareUpdate(graph,
                PATH_SPARQL_QUERY_TS_TEMPLATE.format(c),
                {"aInstance": instance},
                False,
                RES_SPARQL_NEW_TS_TEMPLATE.format(c),
                "test_{}_action_instance {}".format(action.type.value,c.upper()),
                ignore=["ts"],
                prefixes=WotPrefs):
            return False
    return True

class TestCase3_Subscriptions(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.engine = Engine()
    
    def test_0(self):
        """ 
        The procedure to test the action request/response sequence is the following.
        Given the standard content of the RDF store, we update a new action instance. 
        We then check that the subscription query contains all data required. 
        We add also timestamps, that are necessary items for the following steps.
        Outputs, if present, are checked.
        Delete is then performed.
        
        Consider that the update "new_empty_action_instance.sparql" is used also for output actions,
        and that "new_i_action_instance.sparql" is used also for input-output actions.
        
        The action here tested is Input-Output, which means we test all kind i-o-io actions in one.
        We test also the empty action.
        """
        actions = [ Action.buildFromQuery(self.engine,"<http://MyFirstWebThing.com/Action1>"),
                    Action.buildFromQuery(self.engine,"<http://MyThirdWebThing.com/Action1>")]

        print("\nTest action instance")
        
        # Adding the instances
        for action in actions:
            bindings = {   "thing": action.thing,
                            "action": action.uri,
                            "newAInstance": action.uri.replace(">","/instance1>"),
                            "newAuthor": "<http://MySecondWebThing.com>",
                            "newIData": action.uri.replace(">","/instance1/InputData>"),
                            "newIValue": "This is an input string",
                            "newIDS": action.uri.replace(">","/DataSchema/input>")}
            instance = action.newRequest(bindings)
            
            # Workaround for test functionality avoids isInferred exceptions
            action.action_task = lambda a,r: None

            # Checking the instance
            self.assertTrue(utils.query_CompareUpdate(self.engine,
                PATH_SPARQL_QUERY_ACTION_INSTANCE,
                bindings,
                False,
                RES_SPARQL_NEW_ACTION_INSTANCE_TEMPLATE.format(action.type.value),
                "test_{}_action_instance UPDATE-SUBSCRIBE".format(action.type.value),
                ignore=["aTS"],
                prefixes=WotPrefs))
                
            # Adding and checking Confirmation and Completion timestamps
            self.assertTrue(add_action_instance_ts(self.engine,instance,action))
            
            # Update the instances
            bindings["newAInstance"] = action.uri.replace(">","/instance2>")
            if action.type == AType.INPUT_ACTION:
                bindings["newIData"] = action.uri.replace(">","/instance2/InputData>")
                bindings["newIValue"] = "This is a modified input string"
            # Workaround for test functionality avoids isInferred exceptions
            action.action_task = None
            instance = action.newRequest(bindings)

            # Checking updates to instances are successful
            self.assertTrue(utils.query_CompareUpdate(self.engine,
                PATH_SPARQL_QUERY_ACTION_INSTANCE,
                bindings,
                False,
                RES_SPARQL_NEW_ACTION_INSTANCE_UPDATE_TEMPLATE.format(action.type.value),
                "test_{}_action_instance NEW REQUEST".format(action.type.value),
                ignore=["aTS"],
                prefixes=WotPrefs))
            
            # Adding and checking Confirmation and Completion timestamps
            # Workaround for test functionality avoids isInferred exceptions
            action.action_task = lambda a,r: None
            self.assertTrue(add_action_instance_ts(self.engine,instance,action))
            
            if action.type == AType.INPUT_ACTION:
                # Post output
                # Workaround for test functionality avoids isInferred exceptions
                action.action_task = None
                action.post_output({"instance": instance,
                                    "oData": action.uri.replace(">","/instance2/OutputData"),
                                    "oValue": "my output value",
                                    "oDS": action.uri.replace(">","/DataSchema/output")})
                # Check it
                self.assertTrue(utils.query_CompareUpdate(self.engine,
                    PATH_SPARQL_QUERY_INSTANCE_OUTPUT,
                    {"instance": bindings["newAInstance"]},
                    False,
                    RES_SPARQL_NEW_INSTANCE_OUTPUT,
                    "test_{}_action_instance OUTPUT".format(URIS[action].value),
                    prefixes=WotPrefs))
        
            # Remove instances and outputs
            action.deleteInstance(instance)
        
        self.assertTrue(utils.query_FileCompare(self.engine,fileAddress=RES_SPARQL_QUERY_ALL,message="test_action_instance DELETE INSTANCE"))
        reset_testbase(self.engine)
        
    def test_1(self):
        """ 
        The procedure to test the event throwing/receive sequence is the following.
        Given the standard content of the RDF store, we update a new event instance. 
        We then check that the subscription query contains all data required. 
        Outputs, if present, are checked.
        Delete is then performed.
        """
        events = [  Event.buildFromQuery(self.engine,"<http://MyFirstWebThing.com/Event1>"),
                    Event.buildFromQuery(self.engine,"<http://MyThirdWebThing.com/Event1>")]
                    
        print("\nTest event instances")
        
        # Adding the instances
        for event in events:
            bindings = {"thing": event.thing,
                        "event": event.uri,
                        "newEInstance": event.uri.replace(">","/instance1>"),
                        "newOData": event.uri.replace(">","/instance1/OutputData>"),
                        "newValue": "2018-06-23T10:05:19.478Z",
                        "newDS": event.uri.replace(">","/DataSchema/output>")}
            instance = event.notify(bindings)

            # Checking the instance
            self.assertTrue(utils.query_CompareUpdate(self.engine,
                PATH_SPARQL_QUERY_EVENT_INSTANCE,
                bindings,
                False,
                RES_SPARQL_NEW_EVENT_INSTANCE_TEMPLATE.format(event.type.value),
                "test_{}_event_instance UPDATE-SUBSCRIBE".format(event.type.value),
                ignore=["eTS"],
                prefixes=WotPrefs))
                        
            # Update the instances
            bindings["newEInstance"] = event.uri.replace(">","/instance2>")
            if event.type is EType.OUTPUT_EVENT:
                bindings["newOData"] = event.uri.replace(">","/instance2/OutputData>")
                bindings["newValue"] = "2018-06-23T17:05:19.478Z"
            instance = event.notify(bindings)

            # Checking updates to instances are successful
            self.assertTrue(utils.query_CompareUpdate(self.engine,
                PATH_SPARQL_QUERY_EVENT_INSTANCE,
                bindings,
                False,
                RES_SPARQL_NEW_EVENT_INSTANCE_UPDATE_TEMPLATE.format(event.type.value),
                "test_{}_event_instance NEW REQUEST".format(event.type.value),
                ignore=["eTS"],
                prefixes=WotPrefs))
        
            # Remove instances and outputs
            event.deleteInstance(instance)
        
        self.assertTrue(utils.query_FileCompare(self.engine,fileAddress=RES_SPARQL_QUERY_ALL,message="test_event_instance DELETE INSTANCE",show_diff=True))
        reset_testbase(self.engine)

if __name__ == '__main__':
    unittest.main(failfast=True)
