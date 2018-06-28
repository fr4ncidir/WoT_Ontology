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
    """
    wot:Action python implementation
    """
    def __init__(self,sepa,bindings,action_task,forProperties=[],force_type=None):
        """
        Constructor of Action Item. 
        'sepa' is the blazegraph/sepa instance.
        'bindings' is a dictionary formatted as required by the new-action yaml
        'action_task' is the function that is triggered when the action is requested. When
            the Action is built from a query with the 'buildFromQuery' method, this field is
            left None. In this case, we say that the Action is 'inferred', and some 
            methods throw exception.
        'forProperties' is a list containing the Properties that are linked to this action
        'force_type' is a flag which you can use to force the type of the action into IO, O, I, EMPTY.
            To do so, use the AType enum.
        """
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
        
    def set_action_task(self,new_action_task):
        self._action_task = new_action_task
    
    def post(self):
        """
        This method is not available if the Action is inferred.
        Posts the Action to the rdf store, together with its forced bindings.
        """
        assert not self.isInferred()
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
        """
        TODO This method is not available if the Action is inferred.
        Subscribe to action requests
        """
        assert not self.isInferred()
        # threading.start_new_thread(self._action_task,args)
        
    def disable(self):
        """
        TODO This method is not available if the Action is inferred.
        Unsubscribe to action requests. Action will be disabled until 'enable' is called again
        """
        # unsubscribe to action requests
        assert not self.isInferred()
        
    def post_output(self,bindings):
        """
        TODO This method is not available if the Action is inferred.
        Post to rdf store the output of an action computation
        """
        assert not self.isInferred()
        if (self._type is AType.OUTPUT_ACTION) or (self._type is AType.IO_ACTION):
            sparql,fB = bzu.get_yaml_data(cts.PATH_SPARQL_NEW_INSTANCE_OUTPUT,fB_values=bindings)
            self._sepa.update(sparql,fB)
            self.post_timestamp("completion",instance)
           
    def post_completion(self,instance):
        self._post_timestamp("completion",instance)
        
    def post_confirmation(self,instance):
        self._post_timestamp("confirmation",instance)
    
    def _post_timestamp(self,ts_type,instance):
        assert not self.isInferred()
        if (ts_type.lower() != "completion") and (ts_type.lower() != "confirmation"):
            raise ValueError
        sparql,fB = bzu.get_yaml_data(cts.PATH_SPARQL_NEW_TS_TEMPLATE.format(ts_type.lower()),fB_values={"aInstance": instance})
        self._sepa.update(sparql,fB)
        
    @property
    def type(self):
        return self._type
    
    @classmethod
    def getBindingList(action_type):
        """
        Utility function to know how you have to format the bindings for the constructor.
        DEPRECATED
        """
        if action_type not in AType:
            raise ValueError
        _,fB = bzu.get_yaml_data(cts.PATH_SPARQL_NEW_ACTION_TEMPLATE.format(action_type.value))
        return fB.keys()
        
    @staticmethod
    def discover(sepa,action="UNDEF",nice_output=False):
        """
        Static method, used to discover actions in the rdf store.
        'action' by default is 'UNDEF', retrieving every action. Otherwise it will be more selective
        'nice_output' prints a nice table on console, using tablaze.
        """
        sparql,fB = bzu.get_yaml_data(cts.PATH_SPARQL_QUERY_ACTION,fB_values={"action_uri":action})
        d_output = sepa.query(sparql,fB=fB)
        if nice_output:
            bzu.tablify(json.dumps(d_output))
        if ((action != "UNDEF") and (len(d_output["results"]["bindings"])>1)):
            raise Exception("Action discovery gave more than one result")
        return d_output
    
    @staticmethod
    def buildFromQuery(sepa,actionURI):
        """
        Static method to build an inferred local copy of an action by querying the rdf store.
        'actionURI' is the uri of the action needed.
        """
        query_action = Action.discover(sepa,action=actionURI)
        query_ip = InteractionPattern.discover(sepa,ip_type="wot:Action",nice_output=False)
        for binding in query_ip["results"]["bindings"]:
            if binding["ipattern"]["value"] == actionURI.replace("<","").replace(">",""):
                td = bzu.uriFormat(binding["td"]["value"])
        aBinding = query_action["results"]["bindings"][0]
        out_bindings = { "td": td,
                        "action": bzu.uriFormat(aBinding["action"]["value"]),
                        "newName": aBinding["aName"]["value"]}
        if "oDS" in aBinding.keys():
            out_bindings["ods"] = bzu.uriFormat(aBinding["oDS"]["value"])
        if "iDS" in aBinding.keys():
            out_bindings["ids"] = bzu.uriFormat(aBinding["iDS"]["value"])
        query_thing = Thing.discover(sepa,bindings={"td_uri": td})
        out_bindings["thing"] = bzu.uriFormat(query_thing["results"]["bindings"][0]["thing"]["value"])
        return Action(sepa,out_bindings,None)
    
    @staticmethod
    def newRequest(sepa,bindings,a_type):
        """
        Used by clients, this method allows to ask to perform an action.
        'bindings' contains the information needed by the new-action-instance sparql
        'a_type' is the corresponding AType enum item.
        Returns the instance uri.
        """
        r_type = a_type.value
        if a_type is AType.IO_ACTION:
            r_type = AType.INPUT_ACTION.value
        if a_type is AType.OUTPUT_ACTION:
            r_type = AType.EMPTY_ACTION.value
        sparql,fB = bzu.get_yaml_data(cts.PATH_SPARQL_NEW_ACTION_INSTANCE_TEMPLATE.format(r_type), fB_values=bindings)
        sepa.update(sparql,fB)
        return bindings["newAInstance"]
            
    def isInferred(self):
        if self._action_task is None:
            return True
        return False
        
    def deleteInstance(self,instance):
        super().deleteInstance(instance)
        assert not self.isInferred()
        sparql,fB = bzu.get_yaml_data(cts.PATH_SPARQL_DELETE_ACTION_INSTANCE,fB_values={"aInstance": instance})
        self._sepa.update(sparql,fB)
