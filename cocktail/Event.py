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

import cocktail.InteractionPattern as InteractionPattern
import sparql_utilities as bzu
import constants as cts
from enum import Enum

class EType(Enum):
    OUTPUT_EVENT = "o"
    EMPTY_EVENT = "empty"

class Event(InteractionPattern):
    def __init__(self,sepa,bindings,forProperties=[]):
        super().__init__(sepa,bindings)
        if "ods" in bindings.keys(bindings):
            self._type = EType.OUTPUT_EVENT
        else:
            self._type = EType.EMPTY_EVENT
        self._forProperties = forProperties
        
    def post():
        sparql,fB = bzu.get_yaml_data(cts.PATH_SPARQL_NEW_EVENT_TEMPLATE.format(self.type),fB_values=self._bindings)
        self._sepa.update(sparql,fB)
        
        sparql,fB = bzu.get_yaml_data(cts.PATH_SPARQL_ADD_FORPROPERTY)
        properties = []
        for prop in forProperties:
            properties.append(prop.bindings["property"])
        sparql = sparql.replace("?ip wot:forProperty ?property","?ip wot:forProperty {}".format(", ".join(properties))
        sparql = sparql.replace("?property a wot:Property"," a wotProperty. ".join(properties)+" a wot:Property")
        self._sepa.update(sparql,fB)
        
    def notify(self,output={}):
        # build fB_values with output
        sparql,fB = bzu.get_yaml_data(cts.PATH_SPARQL_NEW_EVENT_INSTANCE_TEMPLATE.format(self.type),fB_values=self._bindings)
        self._sepa.update(sparql,fB)
    
    @property
    def type(self):
        return self._type
    
    @classmethod
    def getBindingList(event_type):
        if event_type not in EType:
            raise ValueError
        _,fB = bzu.get_yaml_data(cts.PATH_SPARQL_NEW_EVENT_TEMPLATE.format(event_type))
        return fB.keys()
