#!/usr/bin/env python

import sys
sys.path.append("/home/tarsier/Documents/Work/WoT_Ontology")

from cocktail.Thing import Thing
from cocktail.DataSchema import DataSchema
from cocktail.Property import Property
from cocktail.Action import Action
from cocktail.Event import Event

import rlcompleter
import readline
import json

targets = ["all"]

def complete(text, state):
    if text == "":
        matches = targets
    else:
        matches = [x for x in targets if x.startswith(text)]
    if state > len(matches):
        return None
    else:
        return matches[state]

def discovery(sepa,item,instances):
    output = []
    for item in ([item] if item != "i-patterns" else ["actions","events","properties"]):
        if item == "things":
            query = Thing.discover(sepa,nice_output=True)
            for thing in query["results"]["bindings"]:
                output.append(Thing(sepa,{  "thing": thing["thing"]["value"],
                                "newName": thing["name"]["value"],
                                "newTD": thing["td"]["value"]}))
        elif item == "actions":
            query = Action.discover(sepa,nice_output=True)
            for action in query["results"]["bindings"]:
                bindings = { "td": "",
                            "action": action["action"]["value"],
                            "newName": action["aName"]["value"]}
                if "iDS" in action.keys():
                    bindings["ids"] = action["iDS"]["value"]
                if "oDS" in action.keys():
                    bindings["ods"] = action["oDS"]["value"]
                output.append(Action(sepa,bindings,lambda: None))
        elif item == "events":
            query = Event.discover(sepa,nice_output=True)
            for event in query["results"]["bindings"]:
                bindings = { "td": "",
                        "event": event["event"]["value"],
                        "eName": event["eName"]["value"]}
                if "oDS" in event.keys():
                    bindings["ods"] = event["oDS"]["value"]
                output.append(Event(sepa,bindings))
        elif item == "properties":
            query = Property.discover(sepa,nice_output=True)
            for prop in query["results"]["bindings"]:
                bindings = { "td": "",
                    "property": prop["property"]["value"],
                    "newName": prop["pName"]["value"],
                    "newStability": prop["pStability"]["value"],
                    "newWritability": prop["pWritability"]["value"],
                    "newDS": prop["pDS"]["value"],
                    "newPD": "",
                    "newValue": prop["pValue"]["value"]}
                output.append(Property(sepa,bindings))
        elif item == "dataschemas":
            query = DataSchema.discover(sepa,nice_output=True)
            for ds in query["results"]["bindings"]:
                output.append(DataSchema(sepa, {  "ds_uri": query["ds"]["value"],
                                    "fs_uri": query["fs"]["value"],
                                    "fs_types": query["fs_type"]["value"]+", wot:FieldSchema"}))
    return output
        
def describe(sepa,item,instances):
    global targets
    back_exit = set(["back","exit"])
    readline.parse_and_bind("tab: complete")
    readline.set_completer(complete)
    
    objType = {"things": Thing,"actions": Action,"events": Event,"properties": Property, "dataschemas": DataSchema}
    if set(instances) == back_exit:
        print("Please discover first!")
        return "back"
    else:
        targets = ["all"]
        for element in instances:
            if ((not (element in back_exit)) and (type(element) == objType[item])):
                targets.append(element.uri)
        if targets == ["all"]:
            print("No target available")
            return "back"
        else:
            print("Available targets:")
            for target in targets:
                print(target)
            t = input("(describe - {} - choose) > ".format(item))
            if t in back_exit:
                return t
        for targetName in ([t] if t != "all" else objType.keys()):
            found = False
            for element in instances:
                if ((not (element in back_exit)) and 
                    (((targetName in objType.keys()) and (type(element) == objType[targetName])) or
                    (element.uri == targetName))): 
                    found = True
                    print(element.bindings)
                    break
            if not found:
                print("'{}' is not in the available list".format(targetName))
        return t

def getForProperties(sepa):
    ask_forProp = input("(forproperties) > Do you need to appen forProperties? (y/n) ")
    if ask_forProp.lower() == "n":
        return []
    prop_discovery = discovery(sepa,"properties",[])
    for number,prop in enumerate(prop_discovery):
        print("{}: {}".format(number,prop.uri))
    print("Insert the corresponding numbers, separated by space")
    indexes = input("(forproperties - property index) > ").split(" ")
    result = []
    for number,prop in enumerate(prop_discovery):
        if len(indexes)<number:
            break
        if number in indexes:
            result.append(prop)
    return result
    
def create(sepa,item,instances):
    if item == "things":
        ask_superthing = input("(new thing) superthing (n/<uri>): ")
        superthing = None if ask_superthing.lower() == "n" else ask_superthing 
        Thing(sepa,{"thing": input("(new thing) URI: "),
                    "newName": input("(new thing) NAME: "),
                    "newTD": input("(new thing) TD: ")},superthing=superthing).post()
    elif item == "actions":
        bindings = { "td": input("(new action) TD: "),
                        "action": input("(new action) URI: "),
                        "newName": input("(new action) NAME: ")}
        ids = input("(new action) INPUT DS (n/<uri>): ")
        if ids.lower() != "n":
            bindings["ids"] = ids
        ods = input("(new action) OUTPUT DS (n/uri): ")
        if ods.lower() != "n":
            bindings["ods"] = ods
        Action(sepa,bindings,lambda: print("ACTION "+bindings["newName"]+" called."),
            forProperties=getForProperties(sepa)).post()
    elif item == "events":
        bindings = { "td": input("(new event) TD: "),
                        "event": input("(new event) URI: "),
                        "eName": input("(new event) NAME: ")}
        ods = input("(new action) OUTPUT DS (n/uri): ")
        if ods.lower() != "n":
            bindings["ods"] = ods
        Event(sepa,bindings,forProperties=getForProperties(sepa)).post()
    elif item == "properties":
        bindings = { "td": input("(new property) TD: "),
                    "property": input("(new property) URI: "),
                    "newName": input("(new property) NAME: "),
                    "newStability": input("(new property) STABILITY: "),
                    "newWritability": input("(new property) WRITABILITY: "),
                    "newDS": input("(new property) PROPERTY DS: "),
                    "newPD": input("(new property) PROPERTY DATA: "),
                    "newValue": input("(new property) VALUE: ")}
        Property(sepa,bindings).post()
    elif item == "dataschemas":
        DataSchema(graph, { "ds_uri": input("(new dataschema) URI: "),
                    "fs_uri": input("(new dataschema) FIELDSCHEMA URI: "),
                    "fs_types": input("(new dataschema) FIELDSCHEMA TYPES: ")}).post()
                    
def observe_event(sepa,eventUri):
    from threading import Thread
    def observing_function(event_uri):
        from subprocess import call
        call(["xterm", "-hold", "-e", "python3", "/home/tarsier/Documents/Work/WoT_Ontology/wot_monitor/observe_event.py", event_uri])
    Thread(target=observing_function, args=(eventUri, )).start()
    return True
    
    