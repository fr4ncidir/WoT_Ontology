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

from cocktail.InteractionPattern import InteractionPattern
import sparql_utilities as bzu
import constants as cts

class Property(InteractionPattern):
    def __init__(self,sepa,bindings):
        super().__init__(sepa,bindings)
        
    def post(self):
        sparql,fB = bzu.get_yaml_data(cts.PATH_SPARQL_NEW_PROPERTY,fB_values=self._bindings)
        self._sepa.update(sparql,fB)
        return self
        
    def update(self,bindings):
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
