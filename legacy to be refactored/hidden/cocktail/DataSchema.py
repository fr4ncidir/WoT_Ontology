#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  InteractionPattern.py
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

from constants import PATH_SPARQL_NEW_DATASCHEMA, PATH_SPARQL_QUERY_DATASCHEMA
from constants import SPARQL_PREFIXES as WotPrefs
from constants import PATH_SPARQL_NEW_PROPERTY

import sepy.utils as utils
from sepy.YSparqlObject import YSparqlObject as YSparql
from sepy.tablaze import tablify

import logging

logger = logging.getLogger("cocktail_log") 

class DataSchema:
    """
    wot:DataSchema python implementation
    """
    def __init__(self,sepa,bindings):
        self._sepa = sepa
        self._bindings = bindings
        
    @property
    def bindings(self):
        return self._bindings
        
    @property
    def uri(self):
        return self._bindings["ds_uri"]

    def post(self):
        sparql,fB = YSparql(PATH_SPARQL_NEW_DATASCHEMA,external_prefixes=WotPrefs).getData(fB_values=self._bindings)
        self._sepa.update(sparql,fB)
        return self
        
    @staticmethod
    def getBindingList():
        _,fB = YSparql(PATH_SPARQL_NEW_PROPERTY).getData()
        return fB.keys()
    
    @staticmethod
    def discover(sepa,ds="UNDEF",nice_output=False):
        sparql,fB = YSparql(PATH_SPARQL_QUERY_DATASCHEMA,external_prefixes=WotPrefs).getData(fB_values={"ds_force": ds})
        d_output = sepa.query(sparql,fB)
        if nice_output:
            tablify(d_output,prefix_file=WotPrefs.split("\n"))
        return d_output

    def delete(self):
        # TODO
        pass
