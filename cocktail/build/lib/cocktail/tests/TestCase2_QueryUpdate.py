#!/usr/bin python3
# -*- coding: utf-8 -*-
#
#  test_1_queries.py
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

def reset_testbase(graph):
    graph.clear()
    graph.update(y2str(SPARQL_INSERT_THING1))
    graph.update(y2str(SPARQL_INSERT_THING2))
    graph.update(y2str(SPARQL_INSERT_THING3))
    
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

class TestCase2_QueryUpdate(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.engine = Engine()
        
    def setUp(self):
        self.test_0()
        
    def test_0(self):
        try:
            self.engine.query_all()
        except Exception as e:
            self.skipTest(str(e))
        
    def test_1(self):
        # reset the rdf store, puts the 3 test web things and checks
        print("\nRDF store reset; test backgroung setup and check")
        reset_testbase(self.engine)
        self.assertTrue(utils.query_FileCompare(self.engine,fileAddress=RES_SPARQL_QUERY_ALL))
        
    def test_2(self):
        """
        This function performs all the queries available in ./queries folder, and checks the
        corresponding result if there is coincidence. In case of reset==True, results file are 
        rewritten.
        True or False is returned for success or failure.
        """
        from pkg_resources import resource_filename
        from cocktail import __name__ as cName
        import os
        print("\nQueries check")
        # listing all files in ./queries, filtering hidden (starting with '.') and directories
        dir_path = resource_filename(cName,"queries/")
        for fileName in list(filter(lambda myfile: not (myfile.startswith(".") or os.path.isdir(dir_path+myfile)),os.listdir(dir_path))):
            self.assertTrue(utils.query_CompareUpdate(self.engine,
                dir_path+fileName,
                {}, False,
                (dir_path+"results/res_{}").format(fileName).replace(".sparql",".json"),
                log_message=fileName,
                prefixes=WotPrefs))
    
    def test_3(self):
        """
        This function performs checks for adding and removing all is needed for a new web thing.
        In case reset==True, the specific thing query result file is rebuilt.
        True or False is returned for success or failure.
        """
        print("\nTest new thing")
        SUPERTHING = "<http://MyFirstWebThing.com>"
        THING_URI = "<http://TestThing.com>"

        # Adding new thing within the forced bindings
        dummyThing = Thing(self.engine,{"thing": THING_URI,"newName": "TEST-THING","newTD": "<http://TestTD.com>" },superthing=SUPERTHING).post()
        
        self.assertTrue(utils.query_CompareUpdate(self.engine,
            PATH_SPARQL_QUERY_THING,
            {}, False,
            RES_SPARQL_NEW_THING,
            "test_thing ADD",
            replace={"(?thing_uri ?name_literal ?td_uri)": "({} ?name_literal ?td_uri) ({} ?name_literal ?td_uri)".format(THING_URI,SUPERTHING)},
            prefixes=WotPrefs))
            
        # Passing through this point also in reset case allows not to refresh the RDF store into the following test.
        # Deleting the thing, and checking if the triples in all the store are the same as if all the test never happened
        dummyThing.delete()

        # With this line, if it outputs True, we certify that the contents of the RDF store are exactly the same as they were
        # at the beginning of this function. So, no need to call reset_testbase
        self.assertTrue(utils.query_FileCompare(self.engine,message="test_thing DELETE",fileAddress=RES_SPARQL_QUERY_ALL))
        
    def test_4(self):
        """
        This function performs checks for adding, updating and removing a new Property to a web thing.
        Notice that to do so, it is required to test also DataSchema and FieldSchema updates. Those two classes
        are not made to be removed, because they can always be used by other things. 
        
        TODO The procedure to remove them is more complex and involves some queries before performing the delete.
        
        In case reset==True, check jsons are updated. However, the plain 'res_query_all' is not overwritten, because
        the presence of new DataSchema and FieldSchema here requires the existance of a different file named
        'res_query_all_new_dataschema.json'.
        
        True or False is returned for success or failure.
        """
        THING_URI = "<http://TestThing.com>"
        DATASCHEMA_URI = "<http://TestThing.com/Property1/DataSchema/property>"
        PROPERTY_URI = "<http://TestProperty.com>"
        NEW_PROPERTY_VALUE = "HIJKLMNOP"
        TEST_TD = "<http://TestTD.com>"
        
        print("\nTest new Property")
        self.assertTrue(utils.query_FileCompare(self.engine,fileAddress=RES_SPARQL_QUERY_ALL,message="test_property start check"))

        # Adding new Dataschema and its corresponding FieldSchema
        dummy_DS = DataSchema(self.engine, {  "ds_uri": DATASCHEMA_URI,
                                        "fs_uri": "xsd:string",
                                        "fs_types": "xsd:_, wot:FieldSchema"}).post()
        
        # Adding the new thing
        dummyThing = Thing(self.engine,{"thing": THING_URI,"newName": "TEST-THING","newTD": TEST_TD }).post()
        # Adding the property
        p_fBindings = { "td": TEST_TD,
                        "property": PROPERTY_URI,
                        "newName": "TEST-PROPERTY",
                        "newStability": "1",
                        "newWritability": "true",
                        "newDS": DATASCHEMA_URI,
                        "newPD": "<http://TestThing.com/Property1/PropertyData>",
                        "newValue": "ABCDEFG"}
        testProperty = Property(self.engine,p_fBindings).post()
        
        # Querying the property to check it
        sparql,fB = YSparql(queryProperty,external_prefixes=WotPrefs).getData(fB_values={"property_uri": PROPERTY_URI})
        self.assertTrue(utils.query_FileCompare(self.engine,sparql=sparql,fB=fB,message="test_property ADD",fileAddress=RES_SPARQL_NEW_PROPERTY))
        
        # Updating property with a new writability and a new value
        p_fBindings["newWritability"] = "false"
        p_fBindings["newValue"] = NEW_PROPERTY_VALUE
        testProperty.update(p_fBindings)
        
        with open(RES_SPARQL_NEW_PROPERTY,"r") as create:
            jCreate = json.load(create)
            jCreate["results"]["bindings"][0]["pWritability"]["value"] = "false"
            jCreate["results"]["bindings"][0]["pValue"]["value"] = NEW_PROPERTY_VALUE
            with open(RES_SPARQL_NEW_PROPERTY_UPDATE,"r") as update:
                self.assertTrue(utils.notify_result("test_property UPDATE result check",utils.compare_queries(jCreate,json.load(update),show_diff=True)))

        # Performing the query after updates, and check with the update file
        sparql,fB = YSparql(queryProperty,external_prefixes=WotPrefs).getData(fB_values={"property_uri": PROPERTY_URI})
        self.assertTrue(utils.query_FileCompare(self.engine,sparql=sparql,fB=fB,message="test_property UPDATE",fileAddress=RES_SPARQL_NEW_PROPERTY_UPDATE))
        
        # Deleting the property
        testProperty.delete()
        # Query all check
        dummyThing.delete()
        self.assertTrue(utils.query_FileCompare(self.engine,message="test_property DELETE",fileAddress=RES_SPARQL_QUERY_ALL_NEW_DATASCHEMA,show_diff=False))
        reset_testbase(self.engine)
        
    def test_5(self):
        """
        This function performs checks for adding, updating and removing Actions to a web thing.
        Notice that to do so, it is required to test also DataSchema and FieldSchema updates. Those two classes
        are not made to be removed, because they can always be used by other things. 
        
        TODO The procedure to remove them is more complex and involves some queries before performing the delete.
        
        In case reset==True, check jsons are updated. However, the plain 'res_query_all' is not overwritten, because
        the presence of new DataSchema and FieldSchema here requires the existance of a different file named
        'res_query_all_new_dataschema.json'.
        
        True or False is returned for success or failure.
        """
        THING_URI = "<http://TestThing.com>"
        DS_URI_INPUT = "<http://TestThing.com/Actions/DataSchema/input>"
        DS_URI_OUTPUT = "<http://TestThing.com/Actions/DataSchema/output>"
        print("\nTest new actions")
        
        # Adding new Action Dataschemas and its corresponding FieldSchema
        DataSchema(self.engine, { "ds_uri": DS_URI_INPUT,
                        "fs_uri": "xsd:string",
                        "fs_types": "xsd:_, wot:FieldSchema"}).post()
        DataSchema(self.engine, { "ds_uri": DS_URI_OUTPUT,
                        "fs_uri": "xsd:integer",
                        "fs_types": "xsd:_, wot:FieldSchema"}).post()
        
        # Adding the new thing
        dummyThing = Thing(self.engine,{   "thing": THING_URI,
                        "newName": "TEST-THING",
                        "newTD": "<http://TestTD.com>" }).post()
        
        # Adding new Actions and then query the output
        actions = []
        for aType in list(AType):
            actions.append(Action(self.engine,{ "td": "<http://TestTD.com>",
                            "action": "<http://TestAction_{}.com>".format(aType.value),
                            "newName": "TEST-ACTION-{}".format(aType.value),
                            "ids": DS_URI_INPUT,
                            "ods": DS_URI_OUTPUT},lambda: None,force_type=aType).post())
        
        self.assertTrue(utils.query_CompareUpdate(self.engine,
            PATH_SPARQL_QUERY_ACTION,
            {}, False,
            RES_SPARQL_NEW_ACTIONS,
            "test_actions ADD",
            replace={"(?action_uri)": "(<http://TestAction_io.com>) (<http://TestAction_i.com>) (<http://TestAction_o.com>) (<http://TestAction_empty.com>)"},
            prefixes=WotPrefs))
        # Deleting the actions
        for action in actions:
            action.delete()
        # Query all check
        dummyThing.delete()
        self.assertTrue(utils.query_FileCompare(self.engine,message="test_actions DELETE",fileAddress=RES_SPARQL_QUERY_ALL_NEW_DS_ACTIONS))
        reset_testbase(self.engine)
        
    def test_6(self):
        """
        This function performs checks for adding, updating and removing Events to a web thing.
        Notice that to do so, it is required to test also DataSchema and FieldSchema updates. Those two classes
        are not made to be removed, because they can always be used by other things. 
        
        TODO The procedure to remove them is more complex and involves some queries before performing the delete.
        
        In case reset==True, check jsons are updated. However, the plain 'res_query_all' is not overwritten, because
        the presence of new DataSchema and FieldSchema here requires the existance of a different file named
        'res_query_all_new_dataschema.json'.
        
        True or False is returned for success or failure.
        """
        THING_URI = "<http://TestThing.com>"
        DS_URI_OUTPUT = "<http://TestThing.com/Events/DataSchema/output>"
        print("\nTest new events")
        
        # Adding new Action Dataschema and its corresponding FieldSchema
        DataSchema(self.engine, { "ds_uri": DS_URI_OUTPUT,
                    "fs_uri": "xsd:integer",
                    "fs_types": "xsd:_, wot:FieldSchema"}).post()
        
        # Adding the new thing
        dummyThing = Thing(self.engine,{   "thing": THING_URI,
                        "newName": "TEST-THING",
                        "newTD": "<http://TestTD.com>" }).post()
        
        # Adding new Actions and then query the output
        events = []
        for eType in list(EType):
            events.append(Event(self.engine,{ "td": "<http://TestTD.com>",
                            "event": "<http://TestEvent_{}.com>".format(eType.value),
                            "eName": "TEST-EVENT-{}".format(eType.value),
                            "ods": DS_URI_OUTPUT},force_type=eType).post())

        # Querying the actions
        self.assertTrue(utils.query_CompareUpdate(self.engine,
            PATH_SPARQL_QUERY_EVENT,
            {},False,
            RES_SPARQL_NEW_EVENTS,
            "test_events ADD",
            replace={"(?event_uri)": "(<http://TestEvent_o.com>) (<http://TestEvent_empty.com>)"},
            prefixes=WotPrefs))
        
        # Deleting the events
        for event in events:
            event.delete()
        # Query all check
        dummyThing.delete()
        self.assertTrue(utils.query_FileCompare(self.engine,message="test_events DELETE",fileAddress=RES_SPARQL_QUERY_ALL_NEW_DS_EVENTS))
        reset_testbase(self.engine)
        
    def test_7(self):
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
    
    def test_8(self):
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
