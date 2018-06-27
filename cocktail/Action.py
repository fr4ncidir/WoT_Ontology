#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Thing.py
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

from cocktail.InteractionPattern import InteractionPattern
from cocktail.Thing import Thing
import sparql_utilities as bzu
import constants as cts
from enum import Enum
import threading
import logging
import json

#logging.basicConfig(format="%(levelname)s %(asctime)-15s - %s(filename)s - %(message)s",level=logging.INFO)
logger = logging.getLogger("cocktail_log")

class AType(Enum):
    IO_ACTION = "io"
    INPUT_ACTION = "i"
    OUTPUT_ACTION = "o"
    EMPTY_ACTION = "empty"

class Action(InteractionPattern):
    def __init__(self,sepa,bindings,action_task,forProperties=[],force_type=None):
        super().__init__(sepa,bindings)
        self._action_task = action_task
        if (("ods" in bindings.keys()) and ("ids" in bindings.keys())) or (force_type is AType.IO_ACTION):
            self._type = AType.IO_ACTION
        elif ("ods" in bindings.keys()) or (force_type is AType.OUTPUT_ACTION):
            self._type = AType.OUTPUT_ACTION
        elif ("ids" in bindings.keys()) or (force_type is AType.INPUT_ACTION):
            self._type = AType.INPUT_ACTION
        else:
            self._type = AType.EMPTY_ACTION
        self._forProperties = forProperties
    
    @property
    def uri(self):
        return self._bindings["action"]
        
    @property
    def name(self):
        return self._bindings["newName"]
        
    @property
    def action_task(self):
        return self._action_task
        
    def getTD(self)
        return self._bindings["td"]
        
    def setThing(self,thingURI):
        self._bindings["thing"] = thingURI
        
    def getThing(self)
        return self._bindings["thing"] if "thing" in self._bindings.keys() else None
    
    def post(self):
        #assert not self.isInferred()
        sparql,fB = bzu.get_yaml_data(cts.PATH_SPARQL_NEW_ACTION_TEMPLATE.format(self._type.value),fB_values=self._bindings)
        self._sepa.update(sparql,fB)
        
        if self._forProperties:
            sparql,fB = bzu.get_yaml_data(cts.PATH_SPARQL_ADD_FORPROPERTY,fB_values={"ip":self._bindings["action"]})
            properties = []
            for prop in self._forProperties:
                properties.append(prop.bindings["property"])
            sparql = sparql.replace("?ip wot:forProperty ?property","?ip wot:forProperty {}".format(", ".join(properties)))
            sparql = sparql.replace("?property a wot:Property"," a wotProperty. ".join(properties)+" a wot:Property")
            self._sepa.update(sparql,fB)
        return self
        
    def enable(self):
        # Subscribe to action requests
        # at notification, get 'args'
        #assert not self.isInferred()
        # threading.start_new_thread(self._action_task,args)
        pass
        
    def disable(self):
        # unsubscribe to action requests
        #assert not self.isInferred()
        pass
        
    def post_output(self,a_type,instance):
        # this should not be static!
        #assert not self.isInferred()
        if (self._type is AType.OUTPUT_ACTION) or (self._type is AType.IO_ACTION):
            # get bindings
            sparql,fB = bzu.get_yaml_data(cts.PATH_SPARQL_NEW_INSTANCE_OUTPUT,fB_values=self._bindings)
            self._sepa.update(sparql,fB)
            post_timestamp("completion",instance)
           
    def post_timestamp(self,ts_type,instance):
        # this should not be static!!!!
        if (ts_type.lower() != "completion") and (ts_type.lower() != "confirmation"):
            raise ValueError
        sparql,fB = bzu.get_yaml_data(cts.PATH_SPARQL_NEW_TS_TEMPLATE.format(ts_type.lower()),fB_values={"aInstance": instance})
        self._sepa.update(sparql,fB)
        
    @property
    def type(self):
        #assert not self.isInferred()
        return self._type
    
    @classmethod
    def getBindingList(action_type):
        if action_type not in AType:
            raise ValueError
        _,fB = bzu.get_yaml_data(cts.PATH_SPARQL_NEW_ACTION_TEMPLATE.format(action_type.value))
        return fB.keys()
        
    @staticmethod
    def discover(sepa,action="UNDEF",nice_output=True):
        sparql,fB = bzu.get_yaml_data(cts.PATH_SPARQL_QUERY_ACTION,fB_values={"action_uri":action})
        d_output = sepa.query(sparql,fB=fB)
        if nice_output:
            bzu.tablify(json.dumps(d_output))
        if ((action != "UNDEF") and (len(d_output["results"]["bindings"])>1)):
            raise Exception("Action discovery gave more than one result")
        return d_output
    
    @staticmethod
    def buildFromQuery(sepa,actionURI):
        query_action = Action.discover(sepa,action=actionURI)
        query_ip = InteractionPattern.discover(sepa,ip_type="wot:Action")
        for binding in query_ip["results"]["bindings"]:
            if binding["ipattern"] == actionURI:
                td = binding["td"]
        aBinding = query_action["results"]["bindings"][0]
        out_bindings = { "td": td,
                        "action": aBinding["action"],
                        "newName": aBinding["aName"]}
        if "ods" in aBinding.keys():
            out_bindings["ods"] = aBinding["oDS"]
        if "ids" in aBinding.keys():
            out_bindings["ids"] = aBinding["iDS"]
        query_thing = Thing.discover(sepa,bindings={"td_uri": td})
        out_bindings = query_thing["results"]["bindings"][0]["thing_uri"]
        return Action(sepa,out_bindings,None)
    
    @staticmethod
    def newRequest(sepa,bindings,a_type):
        sparql,fB = bzu.get_yaml_data(cst.PATH_SPARQL_NEW_ACTION_INSTANCE_TEMPLATE.format(a_type.value), fB_values=bindings)
        graph.update(sparql,fB)
        return bindings["newAInstance"]
            
    def isInferred(self):
        if self._action_task is None:
            return True
        return False
