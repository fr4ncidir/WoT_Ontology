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
import sparql_utilities as bzu
import constants as cts
from enum import Enum
import threading
import logging

#logging.basicConfig(format="%(levelname)s %(asctime)-15s - %s(filename)s - %(message)s",level=logging.INFO)
logger = logging.getLogger("cocktail_log")

class AType(Enum):
    IO_ACTION = "io"
    INPUT_ACTION = "i"
    OUTPUT_ACTION = "o"
    EMPTY_ACTION = "empty"

class Action(InteractionPattern):
    def __init__(self,sepa,bindings,action_task,forProperties=[]):
        super().__init__(sepa,bindings)
        self._action_task = action_task
        if ("ods" in bindings.keys()) and ("ids" in bindings.keys()):
            self._type = AType.IO_ACTION
        elif "ods" in bindings.keys():
            self._type = AType.OUTPUT_ACTION
        elif "ids" in bindings.keys():
            self._type = AType.INPUT_ACTION
        else:
            self._type = AType.EMPTY_ACTION
        self._forProperties = forProperties
        
    def post():
        sparql,fB = bzu.get_yaml_data(cts.PATH_SPARQL_NEW_ACTION_TEMPLATE.format(self.type),fB_values=self._bindings)
        self._sepa.update(sparql,fB)
        for prop in forProperties:
            # connect property
            break
        
    def enable(self):
        # Subscribe to action requests
        # at notification, get 'args'
        # threading.start_new_thread(self._action_task,args)
        pass
        
    def disable(self):
        # unsubscribe to action requests
        pass
        
    def post_output(self,instance):
        if (self.type is AType.OUTPUT_ACTION) or (self.type is AType.IO_ACTION):
            # get bindings
            sparql,fB = bzu.get_yaml_data(cts.PATH_SPARQL_NEW_INSTANCE_OUTPUT,fB_values=self._bindings)
            self._sepa.update(sparql,fB)
            post_timestamp("completion",instance)
            
    def post_timestamp(self,ts_type,instance):
        if (ts_type.lower() != "completion") and (ts_type.lower() != "confirmation"):
            raise ValueError
        sparql,fB = bzu.get_yaml_data(cts.PATH_SPARQL_NEW_TS_TEMPLATE.format(ts_type.lower()),fB_values={"aInstance": instance})
        self._sepa.update(sparql,fB)
        
    @property
    def type(self):
        return self._type
    
    @classmethod
    def getBindingList(action_type):
        if action_type not in AType:
            raise ValueError
        _,fB = bzu.get_yaml_data(cts.PATH_SPARQL_NEW_ACTION_TEMPLATE.format(action_type))
        return fB.keys()
        
    @classmethod
    def discover(sepa,nice_output=True):
        d_output = sepa.query(cts.PATH_SPARQL_QUERY_ACTION)
        if nice_output:
            bzu.tablify(json.dumps(d_output))
        return d_output
        
    @classmethod
    def newRequest(sepa):
        pass
