#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  wrap_sepa.py
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

from sepy.SEPAClient import *
import logging

logging.basicConfig(format='%(levelname)s %(asctime)-15s %(message)s',level=logging.INFO)  

class Sepa:
    
    def __init__(self,ip="localhost",http_port=8000,ws_port=9000,security={"secure": False, "tokenURI": None, "registerURI": None}):
        self._ip = ip
        self._http_port = http_port
        self._ws_port = ws_port
        self._client = SEPAClient(lastSEPA=True)
        self._security = security
        
    def getIp(self):
        return self._ip
        
    def getPort(self):
        return self._port
        
    @property
    def client(self):
        return self._client
        
    def set_ip(self,ip):
        self._ip = ip
        
    def set_port(self,port):
        self._port = port
        
    def set_security(self,security):
        self._security = security
        
    def query(self,sparql,fB={},destination=None):
        code,output = self._client.query("http://{}:{}/query".format(self._ip,self._http_port),
                            self._bound_sparql(sparql,fB),
                            secure=self._security["secure"],
                            tokenURI=self._security["tokenURI"],
                            registerURI=self._security["registerURI"])
        assert code
        if destination is not None:
            with open(destination,"w") as fileDest:
                print(json.dumps(output),file=fileDest)
        return output
        
    def update(self,sparql,fB={}):
        code,output = self._client.update("http://{}:{}/update".format(self._ip,self._http_port),
                                            self._bound_sparql(sparql,fB),
                                            secure=self._security["secure"],
                                            tokenURI=self._security["tokenURI"],
                                            registerURI=self._security["registerURI"])
        assert code
        return output
        
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

    def subscribe(self,sparql,fB={},alias=None,handler=None):
        return self._client.subscribe("ws://{}:{}/subscribe".format(self._ip,self._ws_port),
                                        self._bound_sparql(sparql,fB),
                                        alias,
                                        handler,
                                        secure=self._security["secure"],
                                        tokenURI=self._security["tokenURI"],
                                        registerURI=self._security["registerURI"])
    
    def unsubscribe(self,subid):
        self._client.unsubscribe(subid,self._securtity["secure"])
