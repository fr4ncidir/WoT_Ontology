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

import sparql_utilities as bzu
import constants as cst
import json

class Thing:
    """
    wot:Thing python implementation
    """
    def __init__(self,sepa,bindings,superthing=None):
        self._bindings = bindings
        self._sepa = sepa
        self._superthing = superthing
        
    def post(self,interaction_patterns=[]):
        """
        Posting the wot:Thing (and its connection to a superthing) with all its interaction patterns.
        """
        sparql,fB = bzu.get_yaml_data(cst.PATH_SPARQL_NEW_THING,fB_values=self._bindings)
        self._sepa.update(sparql,fB)
        if self._superthing is not None:
            sparql,fB = bzu.get_yaml_data(cst.PATH_SPARQL_NEW_SUBTHING, fB_values={"superthing": self._superthing, "subthing": self._bindings["thing"]})
            self._sepa.update(sparql,fB)
        for ip in interaction_patterns:
            ip.post()
        return self
            
    def delete(self):
        sparql,fB = bzu.get_yaml_data(cst.PATH_SPARQL_DELETE_THING, fB_values=self._bindings)
        self._sepa.update(sparql,fB)
        
    @staticmethod
    def discover(sepa,bindings={},nice_output=False):
        """
        Thing discovery. It can be more selective when we use 'bindings', while 'nice_output'
        prints the results to console in a friendly manner.
        """
        sparql,fB = bzu.get_yaml_data(cst.PATH_SPARQL_QUERY_THING, fB_values=bindings)
        d_output = sepa.query(sparql,fB)
        if nice_output:
            bzu.tablify(json.dumps(d_output))
        return d_output
        
    @property
    def bindings(self):
        return self._bindings
