#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  blazegraph.py
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

import requests
import json
import yaml
import logging
import os

prefixes = """prefix xsd: <http://www.w3.org/2001/XMLSchema#>
prefix owl: <http://www.w3.org/2002/07/owl#>
prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
prefix dul: <http://www.ontologydesignpatterns.org/ont/dul/DUL.owl#>
prefix wot: <http://wot.arces.unibo.it/ontology/web_of_things#>
"""

logging.basicConfig(format='%(levelname)s %(asctime)-15s %(message)s',level=logging.INFO)   


def query_blazegraph(args,sparql,forcedbindings={}):
    bound_sparql = sparql
    for key in forcedbindings.keys():
        if ((forcedbindings[key]["type"]=="uri") or (forcedbindings[key]["value"]=="UNDEF")):
            bound_sparql = bound_sparql.replace("?"+key,forcedbindings[key]["value"])
        else:
            bound_sparql = bound_sparql.replace("?"+key,"'"+forcedbindings[key]["value"]+"'")
    try:
        r = requests.post("http://{}:{}/blazegraph/sparql".format(args["ip"],args["port"]), 
                            params={"query":bound_sparql}, 
                            headers={"Accept":"application/sparql-results+json"})
        assert 
    except:
        return None
    return r
    
def update_blazegraph(args,sparql,forcedbindings={}):
    bound_sparql = sparql
    for key in forcedbindings.keys():
        if ((forcedbindings[key]["type"]=="uri") or (forcedbindings[key]["value"]=="UNDEF")):
            bound_sparql = bound_sparql.replace("?"+key,forcedbindings[key]["value"])
        else:
            bound_sparql = bound_sparql.replace("?"+key,"'"+forcedbindings[key]["value"]+"'")
    try:
        r = requests.post("http://{}:{}/blazegraph/sparql".format(args["ip"],args["port"]), 
                            params={"update":bound_sparql})
    except:
        return None
    return r
    
def file_to_string(filepath):
    with open(filepath,"r") as myfile:
        lines = myfile.readlines()
    filtered = list(filter(lambda line: line[0]!="#",lines))
    return "".join(filtered)
    
def json_equal(json_A,json_B):
    try:
        with open(json_A,"r") as jA_file:
            jA = json.load(jA_file)
    except:
        jA = json.loads(json_A)
    try:
        with open(json_B,"r") as jB_file:
            jB = json.load(jB_file)
    except:
        jB = json.loads(json_B)
    return (json.dumps(jA,sort_keys=True) == json.dumps(jB,sort_keys=True))
    
def get_yaml_data(yaml_file):
    textfile = file_to_string(yaml_file)
    yaml_raw = yaml.load(textfile)
    yaml_obj = yaml.dump(yaml_raw)
    yaml_root = yaml_obj[:yaml_obj.index(":")]
    sparql = prefixes + yaml_raw[yaml_root]["sparql"]
    fB = yaml_raw[yaml_root]["forcedBindings"]
    return sparql,fB

#def check_update_delete(update_item,u_fB),(query_item,q_fB),(delete_item,d_fB)):
    #u_sparql,_ = bz.get_yaml_data(update_item)
    #d_sparql,_ = bz.get_yaml_data(delete_item)
    
    #r = bz.update_blazegraph(args,u_sparql,u_fB)
    #assert r.status_code == 200
    
    #query_and_write(query_item,"updates",fB=q_fB)
    
    #r = bz.update_blazegraph(args,d_sparql,d_fB)
    #assert r.status_code == 200
    
    #query_and_check
    #r = bz.query_blazegraph(args,"select * where {?a ?b ?c}")
    #assert r.status_code == 200
    #assert bz.json_equal(r.text,"./queries/results/res_query_all.json") == True
    

def query_and_write(query_item,folder,fB={},forceName=None):
    # query_item can be a plain SPARQL or a path to a yaml file containing the query
    logging.info("Processing {}".format(query_item))
    if os.path.isfile(query_item):
        sparql,_ = get_yaml_data(query_item)
        _,fileName = os.path.split(query_item)
        fileName = fileName.split(".")[0]
    else:
        sparql = query_item
        if forceName is None:
            fileName = input("Please insert file name :")
        else:
            fileName = forceName
    r = query_blazegraph(args,sparql,fB)
    assert r.status_code == 200
    filePath = "./{}/results/res_{}.json".format(folder,fileName)
    logging.info("Writing to {}\n".format(filePath))
    with open(filePath,"w") as myresult:
        myresult.write(r.text)
    return 0
    
def query_and_check(correct_result,query_item,fB={}):
    logging.info("Check on {}".format(correct_result))
    r = query_blazegraph(args,query_item,fB)
    assert r.status_code == 200
    assert json_equal(r.text,correct_result) == True
