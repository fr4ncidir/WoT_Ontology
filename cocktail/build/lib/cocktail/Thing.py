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

import sepy.utils as utils

from .constants import SPARQL_PREFIXES as WotPrefs
from .constants import PATH_SPARQL_NEW_THING as newThing
from .constants import PATH_SPARQL_NEW_SUBTHING as newSubThing
from .constants import PATH_SPARQL_DELETE_THING as delThing
from .constants import PATH_SPARQL_QUERY_THING as queryThing

import logging

from sepy.YSparqlObject import YSparqlObject as YSparql
from sepy.tablaze import tablify

logger = logging.getLogger("cocktail_log") 

class Thing:
    """
    wot:Thing python implementation
    """
    def __init__(self,sepa,bindings,superthing=None):
        """
        Constructor of Thing Item. 
        'sepa' is the blazegraph/sepa instance.
        'bindings' is a dictionary formatted as required by the new-action yaml
        'superthing' is the uri of the superthing that may be required
        """
        self._bindings = bindings
        self._sepa = sepa
        self._superthing = superthing
        
    def post(self,interaction_patterns=[]):
        """
        Posting the wot:Thing (and its connection to a superthing) with all its interaction patterns.
        Note that putting interaction patterns here is not the only way to proceed.
        """
        sparql,fB = YSparql(newThing,external_prefixes=WotPrefs).getData(fB_values=self._bindings)
        self._sepa.update(sparql,fB)
        logger.debug("Posting thing {}: {}".format(self.name, self.uri))
        
        if self._superthing is not None:
            sparql,fB = YSparql(newSubThing,external_prefixes=WotPrefs).getData(fB_values={"superthing": self._superthing, "subthing": self.uri})
            self._sepa.update(sparql,fB)
            logger.debug("Connecting superthing {} to {}".format(self._superthing, self.uri))
        for ip in interaction_patterns:
            logger.debug("Appending interaction pattern {} to {}".format(ip.uri, self.uri))
            ip.post()
        return self
            
    def delete(self):
        """Deletes the thing from the rdf store"""
        sparql,fB = YSparql(delThing,external_prefixes=WotPrefs).getData(fB_values=self._bindings)
        self._sepa.update(sparql,fB)
        logger.debug("Deleting "+self.uri)
        
    @staticmethod
    def discover(sepa,bindings={},nice_output=False):
        """
        Thing discovery. It can be more selective when we use 'bindings', while 'nice_output'
        prints the results to console in a friendly manner.
        """
        sparql,fB = YSparql(queryThing,external_prefixes=WotPrefs).getData(fB_values=bindings)
        d_output = sepa.query(sparql,fB)
        if nice_output:
            tablify(d_output,prefix_file=WotPrefs.split("\n"))
        return d_output
        
    @property
    def bindings(self):
        return self._bindings
        
    @property
    def uri(self):
        return self._bindings["thing"]
        
    @property
    def name(self):
        return self._bindings["newName"]
        
    @property
    def td(self):
        return self._bindings["newTD"]
        
    @property
    def superthing(self):
        return self._superthing
