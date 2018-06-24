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

class InteractionPattern:
    def __init__(self,bindings):
        self._bindings = bindings
        
    @property
    def bindings(self):
        return self._bindings
        
    def delete(sepa):
        sparql,fB = bzu.get_yaml_data(cst.PATH_SPARQL_DELETE_IP,fB_values=bindings)
        sepa.update(sparql,fB)
        
    @abstractmethod
    def post(sepa):
        pass
        
    @abstractmethod
    @staticmethod
    def getBindingList():
        pass
    
    @abstractmethod
    @staticmethod
    def discover(sepa):
        pass
