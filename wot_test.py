#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  wot_test.py
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
#  SEE THE README FOR EXPLANATIONS ON THE TESTS HERE AVAILABLE

import blazegraph as bz
import sparql_utilities as bzu
import json
import logging
import os
import constants as cst
from cocktail.Thing import Thing
from cocktail.DataSchema import DataSchema
from cocktail.Property import Property

logging.basicConfig(format='%(levelname)s %(asctime)-15s %(message)s',level=logging.INFO)
logger = logging.getLogger("ontology_test_log")

THING_URI = "<http://TestThing.com>"

def reset_blazegraph(graph):
    graph.update(cst.SPARQL_DELETE_ALL)
    graph.update(bzu.file_to_string(cst.SPARQL_INSERT_THING1))
    graph.update(bzu.file_to_string(cst.SPARQL_INSERT_THING2))
    graph.update(bzu.file_to_string(cst.SPARQL_INSERT_THING3))
    
def update_dummy_thing(graph):
    Thing(graph,{   "thing": THING_URI,
                    "newName": "TEST-THING",
                    "newTD": "<http://TestTD.com>" }).post()
    
def add_action_instance_ts(graph,instance,iType,reset):
    result = True
    for c in ["confirmation","completion"]:
        sparql,fB = bzu.get_yaml_data(cst.PATH_SPARQL_NEW_TS_TEMPLATE.format(c),fB_values={"aInstance": instance})
        graph.update(sparql,fB)
        
        result = result and bzu.query_CompareUpdate(graph,
            cst.PATH_SPARQL_QUERY_TS_TEMPLATE.format(c),
            {"aInstance": instance},
            reset,
            cst.RES_SPARQL_NEW_TS_TEMPLATE.format(c),
            "test_{}_action_instance {}".format(iType,c.upper()),
            ignore=["ts"])
    return result
    
def test_queries(graph,reset=False):
    """
    This function performs all the queries available in ./queries folder, and checks the
    corresponding result if there is coincidence. In case of reset==True, results file are 
    rewritten.
    True or False is returned for success or failure.
    """
    logger.info("STARTING TEST_QUERIES")
    result = True
    # listing all files in ./queries, filtering hidden (starting with '.') and directories
    for fileName in list(filter(lambda myfile: not (myfile.startswith(".") or os.path.isdir("./queries/"+myfile)),os.listdir("./queries"))):
        result = result and bzu.query_CompareUpdate(graph,
            "./queries/{}".format(fileName),
            {}, reset,
            "./queries/results/res_{}".format(fileName).replace(".sparql",".json"),
            fileName)
    logger.info("ENDING TEST_QUERIES")
    return bzu.notify_result("test_queries",result)

def test_new_thing(graph,reset=False):
    """
    This function performs checks for adding and removing all is needed for a new web thing.
    In case reset==True, the specific thing query result file is rebuilt.
    True or False is returned for success or failure.
    """
    SUPERTHING = "<http://MyFirstWebThing.com>"
    
    logger.info("STARTING TEST_NEW_THING")
    # Adding new thing within the forced bindings
    dummyThing = Thing(graph,{"thing": THING_URI,"newName": "TEST-THING","newTD": "<http://TestTD.com>" },superthing=SUPERTHING)
    dummyThing.post()
    
    # Registering the new thing as subthing of a previous existing one
    # sparql,fB = bzu.get_yaml_data(cst.PATH_SPARQL_NEW_SUBTHING,
        # fB_values={ "superthing": SUPERTHING,
                    # "subthing": THING_URI})
    # graph.update(sparql,fB)
    
    result = bzu.query_CompareUpdate(graph,
        cst.PATH_SPARQL_QUERY_THING,
        {}, reset,
        cst.RES_SPARQL_NEW_THING,
        "test_thing ADD",
        replace={"(?thing_uri ?name_literal ?td_uri)": "({} ?name_literal ?td_uri) ({} ?name_literal ?td_uri)".format(THING_URI,SUPERTHING)})
        
    # Passing through this point also in reset case allows not to refresh the RDF store into the following test.
    # Deleting the thing, and checking if the triples in all the store are the same as if all the test never happened
    dummyThing.delete()
    # sparql,fB = bzu.get_yaml_data(cst.PATH_SPARQL_DELETE_THING, fB_values={"thing": THING_URI})
    # graph.update(sparql,fB)
    # With this line, if it outputs True, we certify that the contents of the RDF store are exactly the same as they were
    # at the beginning of this function. So, no need to call reset_blazegraph
    result = result and bzu.query_FileCompare(graph,message="test_thing DELETE")
    logger.info("ENDING TEST_NEW_THING")
    return result
    
def test_new_property(graph,reset=False):
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
    DATASCHEMA_URI = "<http://TestThing.com/Property1/DataSchema/property>"
    PROPERTY_URI = "<http://TestProperty.com>"
    NEW_PROPERTY_VALUE = "HIJKLMNOP"
    
    logger.info("STARTING TEST_NEW_PROPERTY")
    result = True
    if not (reset or bzu.query_FileCompare(graph,message="test_property start check")):
        # This check is useful only if reset is False.
        logger.error("test_property start check failure: skip")
        return False
    # Adding new Dataschema and its corresponding FieldSchema
    dummy_DS = DataSchema(graph, {   "ds_uri": DATASCHEMA_URI,
                                                "fs_uri": "xsd:string",
                                                "fs_types": "xsd:_, wot:FieldSchema"})
    # sparql,fB = bzu.get_yaml_data(cst.PATH_SPARQL_NEW_DATASCHEMA,
        # fB_values={ "ds_uri": DATASCHEMA_URI,
                    # "fs_uri": "xsd:string",
                    # "fs_types": "xsd:_, wot:FieldSchema"})
    # graph.update(sparql,fB)

    if reset:
        logger.warning("Rebuilding "+cst.RES_SPARQL_QUERY_ALL_NEW_DATASCHEMA)
        graph.query(cst.SPARQL_QUERY_ALL,destination=cst.RES_SPARQL_QUERY_ALL_NEW_DATASCHEMA)
    
    # Adding the new thing
    dummyThing = Thing(graph,{"thing": THING_URI,"newName": "TEST-THING","newTD": "<http://TestTD.com>" })
    
    # Adding the property
    p_fBindings = { "td": "<http://TestTD.com>",
                    "property": PROPERTY_URI,
                    "newName": "TEST-PROPERTY",
                    "newStability": "1",
                    "newWritability": "true",
                    "newDS": DATASCHEMA_URI,
                    "newPD": "<http://TestThing.com/Property1/PropertyData>",
                    "newValue": "ABCDEFG"}
    testProperty = Property(graph,p_fBindings)
    testProperty.post()
    # sparql,fB = bzu.get_yaml_data(cst.PATH_SPARQL_NEW_PROPERTY,fB_values=p_fBindings)
    # graph.update(sparql,fB)
    
    # Querying the property to check it
    sparql,fB = bzu.get_yaml_data(cst.PATH_SPARQL_QUERY_PROPERTY, fB_values={"property_uri": PROPERTY_URI})
    if reset:
        logger.warning("Rebuilding "+cst.RES_SPARQL_NEW_PROPERTY)
        # First property creation query and write result to file
        create = graph.query(sparql,fB=fB,destination=cst.RES_SPARQL_NEW_PROPERTY)
    else:
        result = bzu.query_FileCompare(graph,sparql=sparql,fB=fB,message="test_property ADD",fileAddress=cst.RES_SPARQL_NEW_PROPERTY)
    
    
    # Updating property with a new writability and a new value
    p_fBindings["newWritability"] = "false"
    p_fBindings["newValue"] = NEW_PROPERTY_VALUE
    testProperty.update(p_fBindings)
    # sparql,fB = bzu.get_yaml_data(cst.PATH_SPARQL_NEW_PROPERTY, fB_values=p_fBindings)
    # graph.update(sparql,fB)
    
    # Query again to confirm updates
    sparql,fB = bzu.get_yaml_data(cst.PATH_SPARQL_QUERY_PROPERTY, fB_values={"property_uri": PROPERTY_URI})
    if reset:
        # reset version: just a plain equivalence check:
        # create json is already open and written to file
        logger.warning("Rebuilding "+cst.RES_SPARQL_NEW_PROPERTY_UPDATE)
        # Property update query and write result to file, open it; create redefinition to check
        update = graph.query(sparql,fB=fB,destination=cst.RES_SPARQL_NEW_PROPERTY_UPDATE)
        create["results"]["bindings"][0]["pWritability"]["value"] = "false"
        create["results"]["bindings"][0]["pValue"]["value"] = NEW_PROPERTY_VALUE
        result = bzu.notify_result("test_property UPDATE rebuild",bzu.compare_queries(create,update,show_diff=True))
        if not result:
            logger.error("Rebuild error: files res_new_property_update.json and res_new_property_create.json are not equivalent")
    else:
        # Non reset version of Query again to confirm updates
        try:
            # check results files are correct
            create = open(cst.RES_SPARQL_NEW_PROPERTY,"r")
            update = open(cst.RES_SPARQL_NEW_PROPERTY_UPDATE,"r")
            jCreate = json.load(create)
            jCreate["results"]["bindings"][0]["pWritability"]["value"] = "false"
            jCreate["results"]["bindings"][0]["pValue"]["value"] = NEW_PROPERTY_VALUE
            result = bzu.notify_result("test_property UPDATE result check",bzu.compare_queries(jCreate,json.load(update),show_diff=True))
            create.close()
            update.close()
        except Exception as e:
            logger.error("Error while opening new_property_create or update")
            bzu.notify_result("test_property UPDATE exception",str(e))
            reset_blazegraph(graph)
            return False
        # Performing the query after updates, and check with the update file
        result = result and bzu.query_FileCompare(graph,sparql=sparql,fB=fB,message="test_property UPDATE",fileAddress=cst.RES_SPARQL_NEW_PROPERTY_UPDATE)
        
        # Deleting the property
        testProperty.delete()
        # sparql,fB = bzu.get_yaml_data(cst.PATH_SPARQL_DELETE_IP, fB_values={"ip": PROPERTY_URI})
        # graph.update(sparql,fB)
        
        # Query all check
        dummyThing.delete()
        # sparql,fB = bzu.get_yaml_data(cst.PATH_SPARQL_DELETE_THING, fB_values={"thing": "<http://TestThing.com>"})
        # graph.update(sparql,fB)
        result = result and bzu.query_FileCompare(graph,message="test_property DELETE",fileAddress=cst.RES_SPARQL_QUERY_ALL_NEW_DATASCHEMA,show_diff=False)
    
    reset_blazegraph(graph)
    logger.info("ENDING TEST_NEW_PROPERTY")
    return result
    
def test_new_action(graph,reset=False):
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
    DS_URI_INPUT = "<http://TestThing.com/Actions/DataSchema/input>"
    DS_URI_OUTPUT = "<http://TestThing.com/Actions/DataSchema/output>"
    logger.info("STARTING TEST_NEW_ACTIONS")
    
    # Adding new Action Dataschemas and its corresponding FieldSchema
    sparql,fB = bzu.get_yaml_data(cst.PATH_SPARQL_NEW_DATASCHEMA,
        fB_values={ "ds_uri": DS_URI_INPUT,
                    "fs_uri": "xsd:string",
                    "fs_types": "xsd:_, wot:FieldSchema"})
    graph.update(sparql,fB)
    sparql,fB = bzu.get_yaml_data(cst.PATH_SPARQL_NEW_DATASCHEMA,
        fB_values={ "ds_uri": DS_URI_OUTPUT,
                    "fs_uri": "xsd:integer",
                    "fs_types": "xsd:_, wot:FieldSchema"})
    graph.update(sparql,fB)
    
    if reset:
        logger.warning("Rebuilding "+cst.RES_SPARQL_QUERY_ALL_NEW_DS_ACTIONS)
        graph.query(cst.SPARQL_QUERY_ALL,destination=cst.RES_SPARQL_QUERY_ALL_NEW_DS_ACTIONS)
    
    # Adding the new thing
    update_dummy_thing(graph)
    
    # Adding new Actions and then query the output
    for aType in ["IO","I","O","EMPTY"]:
        sparql,fB = bzu.get_yaml_data(cst.PATH_SPARQL_NEW_ACTION_TEMPLATE.format(aType.lower()),
            fB_values={ "td": "<http://TestTD.com>",
                        "action": "<http://TestAction_{}.com>".format(aType),
                        "newName": "TEST-ACTION-{}".format(aType),
                        "ids": DS_URI_INPUT,
                        "ods": DS_URI_OUTPUT})
        graph.update(sparql,fB)
    
    
    result = bzu.query_CompareUpdate(graph,
        cst.PATH_SPARQL_QUERY_ACTION,
        {}, reset,
        cst.RES_SPARQL_NEW_ACTIONS,
        "test_actions ADD",
        replace={"(?action_uri)": "(<http://TestAction_IO.com>) (<http://TestAction_I.com>) (<http://TestAction_O.com>) (<http://TestAction_EMPTY.com>)"})
    if not reset:
        # Deleting the actions
        for aType in ["IO","I","O","EMPTY"]:
            sparql,fB = bzu.get_yaml_data(cst.PATH_SPARQL_DELETE_IP, fB_values={"ip": "<http://TestAction_{}.com>".format(aType)})
            graph.update(sparql,fB)
        
        # Query all check
        sparql,fB = bzu.get_yaml_data(cst.PATH_SPARQL_DELETE_THING, fB_values={"thing": THING_URI})
        graph.update(sparql,fB)
        result = result and bzu.query_FileCompare(graph,message="test_actions DELETE",fileAddress=cst.RES_SPARQL_QUERY_ALL_NEW_DS_ACTIONS)
    
    reset_blazegraph(graph)
    logger.info("ENDING TEST_NEW_ACTIONS")
    return result

def test_new_event(graph,reset=False):
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
    DS_URI_OUTPUT = "<http://TestThing.com/Events/DataSchema/output>"
    logger.info("STARTING TEST_NEW_EVENTS")
    
    # Adding new Action Dataschema and its corresponding FieldSchema
    sparql,fB = bzu.get_yaml_data(cst.PATH_SPARQL_NEW_DATASCHEMA,
        fB_values={ "ds_uri": DS_URI_OUTPUT,
                    "fs_uri": "xsd:integer",
                    "fs_types": "xsd:_, wot:FieldSchema"})
    graph.update(sparql,fB)
    
    if reset:
        logger.warning("Rebuilding "+cst.RES_SPARQL_QUERY_ALL_NEW_DS_EVENTS)
        graph.query(cst.SPARQL_QUERY_ALL,destination=cst.RES_SPARQL_QUERY_ALL_NEW_DS_EVENTS)
    
    # Adding the new thing
    update_dummy_thing(graph)
    
    # Adding new Actions and then query the output
    for eType in ["O","EMPTY"]:
        sparql,fB = bzu.get_yaml_data(cst.PATH_SPARQL_NEW_EVENT_TEMPLATE.format(eType.lower()),
            fB_values={ "td": "<http://TestTD.com>",
                        "event": "<http://TestEvent_{}.com>".format(eType),
                        "eName": "TEST-EVENT-{}".format(eType),
                        "ods": DS_URI_OUTPUT})
        graph.update(sparql,fB)
    
    # Querying the actions
    result = bzu.query_CompareUpdate(graph,
        cst.PATH_SPARQL_QUERY_EVENT,
        {},reset,
        cst.RES_SPARQL_NEW_EVENTS,
        "test_events ADD",
        replace={"(?event_uri)": "(<http://TestEvent_O.com>) (<http://TestEvent_EMPTY.com>)"})
    
    if not reset:
        # Deleting the actions
        for eType in ["O","EMPTY"]:
            sparql,fB = bzu.get_yaml_data(cst.PATH_SPARQL_DELETE_IP, fB_values={"ip": "<http://TestEvent_{}.com>".format(eType)})
            graph.update(sparql,fB)
        
        # Query all check
        sparql,fB = bzu.get_yaml_data(cst.PATH_SPARQL_DELETE_THING, fB_values={"thing": THING_URI})
        graph.update(sparql,fB)
        result = result and bzu.query_FileCompare(graph,message="test_events DELETE",fileAddress=cst.RES_SPARQL_QUERY_ALL_NEW_DS_EVENTS)
    
    reset_blazegraph(graph)
    logger.info("ENDING TEST_NEW_EVENTS")
    return result

def test_action_instance(graph,reset=False):
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
    URIS = {"<http://MyFirstWebThing.com{}>": "I", "<http://MyThirdWebThing.com{}>": "EMPTY"}
    result = True
    logger.info("STARTING TEST_ACTION_INSTANCE")
    
    # Adding the instances
    for action in URIS.keys():
        bindings = {
                "thing": action.format(""),
                "action": action.format("/Action1"),
                "newAInstance": action.format("/Action1/instance1"),
                "newAuthor": "<http://MySecondWebThing.com>",
                "newIData": action.format("/Action1/instance1/InputData"),
                "newIValue": "This is an input string",
                "newIDS": action.format("/Action1/DataSchema/input")}
        sparql,fB = bzu.get_yaml_data(cst.PATH_SPARQL_NEW_ACTION_INSTANCE_TEMPLATE.format(URIS[action].lower()), fB_values=bindings)
        graph.update(sparql,fB)
        
        # Checking the instance
        result = result and bzu.query_CompareUpdate(graph,
            cst.PATH_SPARQL_QUERY_ACTION_INSTANCE,
            bindings,
            reset,
            cst.RES_SPARQL_NEW_ACTION_INSTANCE_TEMPLATE.format(URIS[action].lower()),
            "test_{}_action_instance UPDATE-SUBSCRIBE".format(URIS[action]),
            ignore=["aTS"])
            
        # Adding and checking Confirmation and Completion timestamps
        result = result and add_action_instance_ts(graph,bindings["newAInstance"],URIS[action],reset)
        
        # Update the instances
        bindings["newAInstance"] = action.format("/Action1/instance2")
        if URIS[action] == "I":
            bindings["newIData"] = action.format("/Action1/instance2/InputData")
            bindings["newIValue"] = "This is a modified input string"
        sparql,fB = bzu.get_yaml_data(cst.PATH_SPARQL_NEW_ACTION_INSTANCE_TEMPLATE.format(URIS[action].lower()), fB_values=bindings)
        graph.update(sparql,fB)
    
        # Checking updates to instances are successful
        result = result and bzu.query_CompareUpdate(graph,
            cst.PATH_SPARQL_QUERY_ACTION_INSTANCE,
            bindings,
            reset,
            cst.RES_SPARQL_NEW_ACTION_INSTANCE_UPDATE_TEMPLATE.format(URIS[action].lower()),
            "test_{}_action_instance NEW REQUEST".format(URIS[action]),
            ignore=["aTS"])
        
        # Adding and checking Confirmation and Completion timestamps
        result = result and add_action_instance_ts(graph,bindings["newAInstance"],URIS[action],reset)
        
        if URIS[action] == "I":
            # Post output
            sparql,fB = bzu.get_yaml_data(cst.PATH_SPARQL_NEW_INSTANCE_OUTPUT,
                        fB_values={ "instance": bindings["newAInstance"],
                                    "oData": action.format("/Action1/instance2/OutputData"),
                                    "oValue": "my output value",
                                    "oDS": action.format("Action1/DataSchema/output")})
            graph.update(sparql,fB)
            
            # Check it
            result = result and bzu.query_CompareUpdate(graph,
                cst.PATH_SPARQL_QUERY_INSTANCE_OUTPUT,
                {"instance": bindings["newAInstance"]},
                reset,
                cst.RES_SPARQL_NEW_INSTANCE_OUTPUT,
                "test_{}_action_instance OUTPUT".format(URIS[action]))
    
        # Remove instances and outputs
        sparql,fB = bzu.get_yaml_data(cst.PATH_SPARQL_DELETE_ACTION_INSTANCE,fB_values={"aInstance": bindings["newAInstance"]})
        graph.update(sparql,fB)
    
    result = result and bzu.query_FileCompare(graph,message="test_action_instance DELETE INSTANCE")
    logger.info("ENDING TEST_ACTION_INSTANCE")
    reset_blazegraph(graph)
    return result

def test_event_instance(graph,reset=False):
    """ 
    The procedure to test the event throwing/receive sequence is the following.
    Given the standard content of the RDF store, we update a new event instance. 
    We then check that the subscription query contains all data required. 
    Outputs, if present, are checked.
    Delete is then performed.
    """
    URIS = {"<http://MyFirstWebThing.com{}>": "O", "<http://MyThirdWebThing.com{}>": "EMPTY"}
    result = True
    logger.info("STARTING TEST_EVENT_INSTANCE")
    
    # Adding the instances
    for event in URIS.keys():
        ev_number = "1" #if event=="O" else "2"
        bindings = {
                "thing": event.format(""),
                "event": event.format("/Event"+ev_number),
                "newEInstance": event.format("/Event"+ev_number+"/instance1"),
                "newOData": event.format("/Event"+ev_number+"/instance1/OutputData"),
                "newValue": "2018-06-23T10:05:19.478Z",
                "newDS": event.format("/Event"+ev_number+"/DataSchema/output")}
        sparql,fB = bzu.get_yaml_data(cst.PATH_SPARQL_NEW_EVENT_INSTANCE_TEMPLATE.format(URIS[event].lower()), fB_values=bindings)
        graph.update(sparql,fB)

        # Checking the instance
        result = result and bzu.query_CompareUpdate(graph,
            cst.PATH_SPARQL_QUERY_EVENT_INSTANCE,
            bindings,
            reset,
            cst.RES_SPARQL_NEW_EVENT_INSTANCE_TEMPLATE.format(URIS[event].lower()),
            "test_{}_event_instance UPDATE-SUBSCRIBE".format(URIS[event]),
            ignore=["eTS"])
                    
        # Update the instances
        bindings["newEInstance"] = event.format("/Event1/instance2")
        if URIS[event] == "O":
            bindings["newOData"] = event.format("/Event1/instance2/OutputData")
            bindings["newValue"] = "2018-06-23T17:05:19.478Z"
        sparql,fB = bzu.get_yaml_data(cst.PATH_SPARQL_NEW_EVENT_INSTANCE_TEMPLATE.format(URIS[event].lower()), fB_values=bindings)
        graph.update(sparql,fB)

        # Checking updates to instances are successful
        result = result and bzu.query_CompareUpdate(graph,
            cst.PATH_SPARQL_QUERY_EVENT_INSTANCE,
            bindings,
            reset,
            cst.RES_SPARQL_NEW_EVENT_INSTANCE_UPDATE_TEMPLATE.format(URIS[event].lower()),
            "test_{}_event_instance NEW REQUEST".format(URIS[event]),
            ignore=["eTS"])
    
        # Remove instances and outputs
        sparql,fB = bzu.get_yaml_data(cst.PATH_SPARQL_DELETE_EVENT_INSTANCE,fB_values={"eInstance": bindings["newEInstance"]})
        graph.update(sparql,fB)
    
    result = result and bzu.query_FileCompare(graph,message="test_event_instance DELETE INSTANCE",show_diff=True)
    logger.info("ENDING TEST_EVENT_INSTANCE")
    return result
