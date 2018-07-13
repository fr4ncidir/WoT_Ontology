#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Property.py
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

import sepy.utils as utils
from sepy.YSparqlObject import YSparqlObject as YSparql
from sepy.tablaze import tablify

from cocktail.InteractionPattern import InteractionPattern

from .constants import PATH_SPARQL_NEW_PROPERTY as newProperty
from .constants import SPARQL_PREFIXES as WotPrefs
from .constants import PATH_SPARQL_QUERY_PROPERTY as queryProperty

import logging

logger = logging.getLogger("cocktail_log") 

class Property(InteractionPattern):
    """
    wot:Property python implementation
    Extends InteractionPattern
    """
    
    def __init__(self,sepa,bindings):
        super().__init__(sepa,bindings)
        
    def post(self):
        """
        Posts the thing to the rdf store.
        """
        logger.info("Posting property {}: {}".format(self.name,self.uri))
        sparql,fB = YSparql(newProperty,external_prefixes=WotPrefs).getData(fB_values=self._bindings)
        self._sepa.update(sparql,fB)
        return self
        
    def update(self,bindings):
        """
        Updates the thing already present in the rdf store.
        """
        self._bindings = bindings
        self.post()
        
    @property
    def uri(self):
        return self._bindings["property"]
        
    @property
    def name(self):
        return self._bindings["newName"]
        
    @property
    def stability(self):
        return self._bindings["newStability"]
    
    @property
    def writability(self):
        return self._bindings["newWritability"]
        
    @property
    def value(self):
        return self._bindings["newValue"]
    
    @classmethod
    def getBindingList():
        _,fB = bzu.get_yaml_data(cts.PATH_SPARQL_NEW_PROPERTY)
        return fB.keys()

    @staticmethod
    def discover(sepa,prop="UNDEF",nice_output=False):
        """
        Static method, used to discover properties in the rdf store.
        'prop' by default is 'UNDEF', retrieving every property. Otherwise it will be more selective
        'nice_output' prints a nice table on console, using tablaze.
        """
        sparql,fB = YSparql(queryProperty,external_prefixes=WotPrefs).getData(fB_values={"property_uri":prop})
        d_output = sepa.query(sparql,fB=fB)
        if nice_output:
            tablify(d_output,prefix_file=WotPrefs.split("\n"))
        if ((prop != "UNDEF") and (len(d_output["results"]["bindings"])>1)):
            raise Exception("Property discovery gave more than one result")
        return d_output
