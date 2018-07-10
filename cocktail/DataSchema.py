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

import constants as cst
import sepy.utils as utils
import json
import logging
from sepy.YSparqlObject import YSparqlObject as YSparql

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
        sparql,fB = YSparql(cst.PATH_SPARQL_NEW_DATASCHEMA,external_prefixes=cst.SPARQL_PREFIXES).getData(fB_values=self._bindings)
        self._sepa.update(sparql,fB)
        return self
        
    @staticmethod
    def getBindingList():
        _,fB = YSparql(cts.PATH_SPARQL_NEW_PROPERTY).getData()
        return fB.keys()
    
    @staticmethod
    def discover(sepa,ds="UNDEF",nice_output=False):
        sparql,fB = YSparql(cst.PATH_SPARQL_QUERY_DATASCHEMA,external_prefixes=cst.SPARQL_PREFIXES).getData(fB_values={"ds_force": ds})
        d_output = sepa.query(sparql,fB)
        if nice_output:
            bzu.tablify(json.dumps(d_output))
        return d_output

    def delete(self):
        # TODO
        pass
