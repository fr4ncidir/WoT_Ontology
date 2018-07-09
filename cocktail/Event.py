#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Event.py
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
import json
import logging

logger = logging.getLogger("cocktail_log") 

class EType(Enum):
    OUTPUT_EVENT = "o"
    EMPTY_EVENT = "empty"

class Event(InteractionPattern):
    """
    wot:Event python implementation
    """
    def __init__(self,sepa,bindings,forProperties=[],force_type=None):
        super().__init__(sepa,bindings)
        if ("ods" in bindings.keys()) or (force_type is EType.OUTPUT_EVENT):
            self._type = EType.OUTPUT_EVENT
        else:
            self._type = EType.EMPTY_EVENT
        self._forProperties = forProperties
        self._observation_subid = None
        
    def post(self):
        sparql,fB = bzu.get_yaml_data(cts.PATH_SPARQL_NEW_EVENT_TEMPLATE.format(self._type.value),fB_values=self._bindings)
        self._sepa.update(sparql,fB)
        
        if self._forProperties:
            sparql,fB = bzu.get_yaml_data(cts.PATH_SPARQL_ADD_FORPROPERTY,fB_values={"ip":self._bindings["event"]})
            properties = []
            for prop in self._forProperties:
                properties.append(prop.bindings["property"])
            sparql = sparql.replace("?ip wot:forProperty ?property","?ip wot:forProperty {}".format(", ".join(properties)))
            sparql = sparql.replace("?property a wot:Property"," a wotProperty. ".join(properties)+" a wot:Property")
            self._sepa.update(sparql,fB)
        return self
        
    def notify(self,bindings):
        """
        Posts to the rdf store a notification, whose data in 'bindings' is formatted as in the new-event-instance yaml.
        """
        sparql,fB = bzu.get_yaml_data(cts.PATH_SPARQL_NEW_EVENT_INSTANCE_TEMPLATE.format(self._type.value),fB_values=bindings)
        self._sepa.update(sparql,fB,show=True)
        return bindings["newEInstance"]
    
    @property
    def uri(self):
        return self._bindings["event"]
        
    @property
    def name(self):
        return self._bindings["eName"]
    
    @property
    def type(self):
        return self._type
    
    @classmethod
    def getBindingList(event_type):
        if event_type not in EType:
            raise ValueError
        _,fB = bzu.get_yaml_data(cts.PATH_SPARQL_NEW_EVENT_TEMPLATE.format(event_type.value))
        return fB.keys()
        
    def deleteInstance(self,instance):
        super().deleteInstance(instance)
        sparql,fB = bzu.get_yaml_data(cts.PATH_SPARQL_DELETE_EVENT_INSTANCE,fB_values={"eInstance": instance})
        self._sepa.update(sparql,fB)
        
    @staticmethod
    def discover(sepa,event="UNDEF",nice_output=False):
        sparql,fB = bzu.get_yaml_data(cts.PATH_SPARQL_QUERY_EVENT,fB_values={"event_uri":event})
        d_output = sepa.query(sparql,fB=fB)
        if nice_output:
            bzu.tablify(json.dumps(d_output))
        if ((event != "UNDEF") and (len(d_output["results"]["bindings"])>1)):
            raise Exception("Event discovery gave more than one result")
        return d_output
        
    @staticmethod
    def buildFromQuery(sepa,eventURI):
        query_event = Event.discover(sepa,event=eventURI)
        query_ip = InteractionPattern.discover(sepa,ip_type="wot:Event",nice_output=False)
        for binding in query_ip["results"]["bindings"]:
            if binding["ipattern"]["value"] == eventURI.replace("<","").replace(">",""):
                td = bzu.uriFormat(binding["td"]["value"])
        eBinding = query_event["results"]["bindings"][0]
        out_bindings = { "td": td,
                        "event": bzu.uriFormat(eBinding["event"]["value"]),
                        "eName": eBinding["eName"]["value"]}
        if "oDS" in eBinding.keys():
            out_bindings["ods"] = bzu.uriFormat(eBinding["oDS"]["value"])
        query_thing = Thing.discover(sepa,bindings={"td_uri": td})
        out_bindings["thing"] = bzu.uriFormat(query_thing["results"]["bindings"][0]["thing"]["value"])
        return Event(sepa,out_bindings)
    
    def observe(self,handler):
        """
        Subscribes to event notifications coming from eventURI.
        'handler' deals with the task to be performed in such situation.
        """
        if self._observation_subid is None:
            sparql,fB = bzu.get_yaml_data(cts.PATH_SPARQL_QUERY_EVENT_INSTANCE,fB_values=self._bindings)
            self._observation_subid = self._sepa.subscribe(sparql,fB=fB,alias=self.uri,handler=handler)
            logger.info("Started observation of {}: id-{}".format(self.uri,self._observation_subid))
        else:
            logger.info("{} already observed".format(self.uri))
        
    def stop_observing(self):
        if self._observation_subid is not None:
            logger.info("Stopped observation of {}: id-{}".format(self.uri,self._observation_subid))
            self._sepa.unsubscribe(self._observation.subid)
            self._observation.subid = None
        else:
            logger.warning("Observation of {} already stopped".format(self.uri))
