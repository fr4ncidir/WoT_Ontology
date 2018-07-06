#!/usr/bin/env python

import sys
sys.path.append("/home/tarsier/Documents/Work/WoT_Ontology")

from cocktail.Thing import Thing
from cocktail.DataSchema import DataSchema
from cocktail.Property import Property
from cocktail.Action import Action
from cocktail.Event import Event

def discovery(sepa,item):
    if item == "things":
        return Thing.discover(sepa,nice_output=True)
    elif item == "actions":
        return Action.discover(sepa,nice_output=True)
    elif item == "events":
        return Event.discover(sepa,nice_output=True)
    elif item == "properties":
        return Property.discover(sepa,ip_type="wot:Property",nice_output=True)
    elif item == "dataschemas":
        pass
        
def describe(sepa,item):
    pass
    
def create(sepa,item):
    pass