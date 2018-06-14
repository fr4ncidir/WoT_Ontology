#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  updateTest.py
#  
#  Copyright 2018 Francesco Antoniazzi <francesco.antoniazzi1991@gmail.com>
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

import blazegraph as bz
import logging

logging.basicConfig(format='%(levelname)s %(asctime)-15s %(message)s',level=logging.INFO)   

class UpdateTest:
    def __init__(self,update_sparql,update_forcedBindings,query_sparql,query_forcedBindings,delete_sparql,delete_forcedBindings):
        _u_sparql = update_sparql
        _u_fB = update_forcedBindings
        _q_sparql = query_sparql
        _q_fB = query_forcedBindings
        _d_sparql = delete_sparql
        _d_fB = delete_forcedBindings
        
    def run(self,graph_address,update_correct,delete_correct):
        r = bz.update_blazegraph(graph_address,self._u_sparql,self._u_fB)
        assert r.status_code == 200
        r = bz.query_blazegraph(graph_address,self._q_sparql,self._q_fB)
        assert r.status_code == 200
        assert bz.json_equal(r.text,update_correct) == True
        
        r = bz.update_blazegraph(graph_address,self._d_sparql,self._d_fB)
        assert r.status_code == 200
        r = bz.query_blazegraph(graph_address,self._q_sparql,self._q_fB)
        assert r.status_code == 200
        return bz.json_equal(r.text,delete_correct) == True
        
    def build(self,graph_address,update_correct,delete_correct):
        r = bz.update_blazegraph(graph_address,self._u_sparql,self._u_fB)
        assert r.status_code == 200
        bz.query_and_write(graph_address,self._q_sparql,"updates",fB=self._q_fB)
        
        r = bz.update_blazegraph(graph_address,self._d_sparql,self._d_fB)
        assert r.status_code == 200
        r = bz.query_blazegraph(graph_address,self._q_sparql,self._q_fB)
        assert r.status_code == 200
        assert bz.json_equal(r.text,delete_correct) == True
