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
from abc import abstractmethod

class InteractionPattern:
    def __init__(self,sepa,bindings):
        self._sepa = sepa
        self._bindings = bindings

    @property
    def bindings(self):
        return self._bindings
        
    def setSepa(self,new_sepa):
        self._sepa = new_sepa
        
    def delete(self):
        sparql,fB = bzu.get_yaml_data(cst.PATH_SPARQL_DELETE_IP,fB_values=self._bindings)
        sepa.update(sparql,fB)
        
    @abstractmethod
    def post(self):
        pass
    
    @classmethod
    @abstractmethod
    def getBindingList():
        pass
    
    @classmethod
    @abstractmethod
    def discover(sepa):
        pass
