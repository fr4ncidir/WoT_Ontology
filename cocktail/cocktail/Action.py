#!/usr/bin python3
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

from .InteractionPattern import InteractionPattern
from .Thing import Thing

import sepy.utils as utils
from sepy.YSparqlObject import YSparqlObject as YSparql
from sepy.tablaze import tablify

from .constants import SPARQL_PREFIXES as WotPrefs
from .constants import PATH_SPARQL_NEW_ACTION_TEMPLATE, PATH_SPARQL_NEW_TS_TEMPLATE, PATH_SPARQL_QUERY_TS_TEMPLATE, PATH_SPARQL_NEW_ACTION_INSTANCE_TEMPLATE
from .constants import PATH_SPARQL_ADD_FORPROPERTY
from .constants import PATH_SPARQL_QUERY_ACTION_INSTANCE, PATH_SPARQL_QUERY_INSTANCE_OUTPUT
from .constants import PATH_SPARQL_NEW_INSTANCE_OUTPUT
from .constants import PATH_SPARQL_DELETE_ACTION_INSTANCE
from .constants import PATH_SPARQL_QUERY_ACTION

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
    wot:Action python implementation.
    Extends InteractionPattern
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
        self._enable_subid = None
    
    @property
    def uri(self):
        return self._bindings["action"]
        
    @property
    def name(self):
        return self._bindings["newName"]
        
    @property
    def action_task(self):
        return self._action_task
    
    @action_task.setter
    def action_task(self,new_action_task):
        self._action_task = new_action_task
    
    def post(self):
        """
        This method is not available if the Action is inferred.
        Posts the Action to the rdf store, together with its forced bindings.
        """
        assert not self.isInferred()
        sparql,fB = YSparql(PATH_SPARQL_NEW_ACTION_TEMPLATE.format(self._type.value),external_prefixes=WotPrefs).getData(fB_values=self._bindings)
        self._sepa.update(sparql,fB)
        logger.debug("Posting action {}: {}".format(self.name,self.uri))
        
        if self._forProperties:
            sparql,fB = YSparql(PATH_SPARQL_ADD_FORPROPERTY,external_prefixes=WotPrefs).getData(fB_values={"ip":self._bindings["action"]},noExcept=True)
            properties = []
            for prop in self._forProperties:
                properties.append(prop.bindings["property"])
                logger.debug("Appending forProperty {} to {}".format(prop.bindings["property"], self.uri))
            sparql = sparql.replace("?ip wot:forProperty ?property","?ip wot:forProperty {}".format(", ".join(properties)))
            sparql = sparql.replace("?property a wot:Property"," a wot:Property. ".join(properties)+" a wot:Property")
            self._sepa.update(sparql,fB)
        return self
        
    def enable(self):
        """
        This method is not available if the Action is inferred.
        Subscribe to action requests
        """
        if self._enable_subid is None:
            assert not self.isInferred()
            logger.info("Enabling Action "+self.uri)
            sparql,fB = YSparql(PATH_SPARQL_QUERY_ACTION_INSTANCE,external_prefixes=WotPrefs).getData(fB_values=self._bindings)
            self._enable_subid = self._sepa.subscribe(sparql,fB=fB,alias=self.uri,handler=self._action_task)
        else:
            logger.warning("{} already enabled".format(self.uri))
        return self
        
    def disable(self):
        """
        This method is not available if the Action is inferred.
        Unsubscribe to action requests. Action will be disabled until 'enable' is called again
        """
        # unsubscribe to action requests
        if self._enable_subid is not None:
            assert not self.isInferred()
            logger.info("Disabling Action "+self.uri)
            self._sepa.unsubscribe(self._enable_subid)
            self._enable_subid = None
        else:
            logger.warning("{} already disabled".format(self.uri))
        
    def post_output(self,bindings):
        """
        This method is not available if the Action is inferred.
        Post to rdf store the output of an action computation
        """
        assert not self.isInferred()
        if (self._type is AType.OUTPUT_ACTION) or (self._type is AType.IO_ACTION):
            logger.debug("Posting output for instance "+bindings["instance"])
            sparql,fB = YSparql(PATH_SPARQL_NEW_INSTANCE_OUTPUT,external_prefixes=WotPrefs).getData(fB_values=bindings)
            self._sepa.update(sparql,fB)
            self.post_completion(bindings["instance"])
           
    def post_completion(self,instance):
        """
        This method is not available if the Action is inferred.
        This method posts completion triple to an action instance
        """
        logger.debug("Posting completion for instance "+instance)
        self._post_timestamp("completion",instance)
        
    def post_confirmation(self,instance):
        """
        This method is not available if the Action is inferred.
        This method posts confirmation triple to an action instance
        """
        logger.debug("Posting confirmation for instance "+instance)
        self._post_timestamp("confirmation",instance)
    
    def _post_timestamp(self,ts_type,instance):
        # This method is not available if the Action is inferred.
        assert not self.isInferred()
        if (ts_type.lower() != "completion") and (ts_type.lower() != "confirmation"):
            raise ValueError("Only 'completion' and 'confirmation' are valid keys")
        sparql,fB = YSparql(PATH_SPARQL_NEW_TS_TEMPLATE.format(ts_type.lower()),external_prefixes=WotPrefs).getData(fB_values={"aInstance": instance})
        self._sepa.update(sparql,fB)
        
    @property
    def type(self):
        """
        Getter for the Action type: IO, EMPTY, I, O
        """
        return self._type
    
    @classmethod
    def getBindingList(self,action_type):
        """
        Utility function to know how you have to format the bindings for the constructor.
        """
        if action_type not in AType:
            raise ValueError
        _,fB = YSparql(PATH_SPARQL_NEW_ACTION_TEMPLATE.format(action_type.value),external_prefixes=WotPrefs).getData()
        return fB.keys()
        
    @staticmethod
    def discover(sepa,action="UNDEF",nice_output=False):
        """
        Static method, used to discover actions in the rdf store.
        'action' by default is 'UNDEF', retrieving every action. Otherwise it will be more selective
        'nice_output' prints a nice table on console, using tablaze.
        """
        sparql,fB = YSparql(PATH_SPARQL_QUERY_ACTION,external_prefixes=WotPrefs).getData(fB_values={"action_uri":action})
        d_output = sepa.query(sparql,fB=fB)
        if nice_output:
            tablify(d_output,prefix_file=WotPrefs.split("\n"))
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
                td = utils.uriFormat(binding["td"]["value"])
        aBinding = query_action["results"]["bindings"][0]
        out_bindings = { "td": td,
                        "action": utils.uriFormat(aBinding["action"]["value"]),
                        "newName": aBinding["aName"]["value"]}
        if "oDS" in aBinding.keys():
            out_bindings["ods"] = utils.uriFormat(aBinding["oDS"]["value"])
        if "iDS" in aBinding.keys():
            out_bindings["ids"] = utils.uriFormat(aBinding["iDS"]["value"])
        query_thing = Thing.discover(sepa,bindings={"td_uri": td})
        out_bindings["thing"] = utils.uriFormat(query_thing["results"]["bindings"][0]["thing"]["value"])
        return Action(sepa,out_bindings,None)
    
    def newRequest(self,bindings,confirm_handler=None,completion_handler=None,output_handler=None):
        """
        Used by clients, this method allows to ask to perform an action.
        'bindings' contains the information needed by the new-action-instance sparql
        Returns the instance uri.
        """
        assert self.isInferred()
        if confirm_handler is not None:
            # in case i'm interested in capturing the confirm flag
            sparql,fB = YSparql(PATH_SPARQL_QUERY_TS_TEMPLATE.format("confirmation"),external_prefixes=WotPrefs).getData(fB_values={"aInstance": bindings["newAInstance"]})
            self._sepa.subscribe(sparql,fB=fB,alias=bindings["newAInstance"],handler=confirm_handler)
        if completion_handler is not None:
            # in case i'm interested in capturing the completion flag
            sparql,fB = YSparql(PATH_SPARQL_QUERY_TS_TEMPLATE.format("completion"),external_prefixes=WotPrefs).getData(fB_values={"aInstance": bindings["newAInstance"]})
            self._sepa.subscribe(sparql,fB=fB,alias=bindings["newAInstance"],handler=completion_handler)
        if output_handler is not None:
            # in case i'm interested in capturing the output
            sparql,fB = YSparql(PATH_SPARQL_QUERY_INSTANCE_OUTPUT,external_prefixes=WotPrefs).getData(fB_values={"instance": bindings["newAInstance"]})
            self._sepa.subscribe(sparql,fB=fB,alias=bindings["newAInstance"],handler=output_handler)
        req_type = AType.INPUT_ACTION.value if (self._type is AType.INPUT_ACTION or self._type is AType.IO_ACTION) else AType.EMPTY_ACTION.value
        sparql,fB = YSparql(PATH_SPARQL_NEW_ACTION_INSTANCE_TEMPLATE.format(req_type),external_prefixes=WotPrefs).getData(fB_values=bindings)
        self._sepa.update(sparql,fB)
        return bindings["newAInstance"]
            
    def isInferred(self):
        """
        An action is 'inferred' when the task to be performed when receiving an instance is None.
        You have an inferred action when you are not the owner of the action, i.e. you just have
        a remote representation of the action, and use it to request instances to the real one
        which is elsewhere and has the action_task filled with a real routine.
        """
        if self._action_task is None:
            return True
        return False
        
    def deleteInstance(self,instance):
        """
        This method is not available if the Action is inferred.
        Deletes the instance from the rdf store.
        """
        super().deleteInstance(instance)
        assert not self.isInferred()
        sparql,fB = YSparql(PATH_SPARQL_DELETE_ACTION_INSTANCE,external_prefixes=WotPrefs).getData(fB_values={"aInstance": instance})
        self._sepa.update(sparql,fB)
