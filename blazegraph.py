#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  blazegraph.py
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

import requests
import logging
import json

logging.basicConfig(format='%(levelname)s %(asctime)-15s %(message)s',level=logging.INFO)   

class Blazegraph:
    """
    Blazegraph class contains the functions needed to perform query and update
    to a Blazegraph instance running somewhere.
    The plain constructor, without arguments, considers localhost:9999 as the target.
    """
    
    def __init__(self,ip="localhost",port=9999):
        self._ip = ip
        self._port = port
        
    def getIp(self):
        return self._ip
        
    def getPort(self):
        return self._port
        
    def query(self,sparql,fB={},destination=None):
        """
        Performs a SPARQL query to the Blazegraph instance.
        - sparql contains the SPARQL string;
        - fB contains the forced bindings;
        - destination, which is usually disabled, redirects the json output 
            of the query into a file
        The same json coming from the query returned to the caller, or None in case
            of exception in http request.
        """
        try:
            r = requests.post("http://{}:{}/blazegraph/sparql".format(self._ip,self._port), 
                            params={"query":self._bound_sparql(sparql,fB)}, 
                            headers={"Accept":"application/sparql-results+json"})
            assert r.status_code == 200
        except Exception as e:
            logging.error("Encountered exception in performing query\n{}\n{}".format(sparql,str(e)))
            return None
        output = json.loads(r.text)
        if destination is not None:
            with open(destination,"w") as fileDest:
                print(json.dumps(output),file=fileDest)
        return output
        
    def update(self,sparql,fB={}):
        """
        Performs a SPARQL update to the Blazegraph instance.
        - sparql contains the SPARQL string;
        - fB contains the forced bindings;
        None is returned in case of exception in http request, and the http output in case
            of success.
        """
        try:
            r = requests.post("http://{}:{}/blazegraph/sparql".format(self._ip,self._port), 
                                params={"update":self._bound_sparql(sparql,fB)})
            assert r.status_code == 200
        except Exception as e:
            logging.error("Encountered exception in performing update\n{}\n{}".format(sparql,str(e)))
            return None
        return r.text
        
    def _bound_sparql(self,sparql,fB):
        """
        This is a private function that makes the substitution into the SPARQL of the forced
        bindings available.
        The complete SPARQL is returned.
        """
        bSparql = sparql
        for key in fB.keys():
            if ((fB[key]["type"]=="uri") or (fB[key]["value"]=="UNDEF")):
                bSparql = bSparql.replace("?"+key,fB[key]["value"])
            else:
                bSparql = bSparql.replace("?"+key,"'"+fB[key]["value"]+"'")
        return bSparql
