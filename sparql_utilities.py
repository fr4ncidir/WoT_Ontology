#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  sparql_utilities.py
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

import yaml
import json
import logging
import os
import constants as cst

"""
This is a utility module with some functions to be used with yaml-formatted jsap.
"""

logging.basicConfig(format="%(levelname)s %(asctime)-15s - %s(filename)s - %(message)s",level=logging.INFO)
logger = logging.getLogger("ontology_test_log")

def notify_result(name,result):
    """
    This function just logs a result in the form
    {name} - {result}
    where name is a string, and result a boolean.
    result is also forwarded to the caller.
    """
    if result:
        logging.info("{} - {}".format(name,result))
    else:
        logging.error("{} - {}".format(name,result))
    return result

def file_to_string(filepath,char_filter="#"):
    """
    Takes a path to file, returns a string containing the file without lines 
    starting with a specific character. Default is '#'
    """
    # Opening file and reading all lines.
    with open(filepath,"r") as myfile:
        lines = myfile.readlines()
    # Removing the lines beginning with the filter character.
    filtered = list(filter(lambda line: line[0]!=char_filter,lines))
    return "".join(filtered)
    
def get_yaml_data(yaml_file,fB_values={}):
    """
    yaml_file parameter is the path to a ysap file.
    fB_values parameter can force values from the defaults in the yaml_file
    The couple SPARQL string, forced binding dictionary is given in return.
    """
    textfile = file_to_string(yaml_file)
    yaml_raw = yaml.load(textfile)
    yaml_obj = yaml.dump(yaml_raw)
    yaml_root = yaml_obj[:yaml_obj.index(":")]
    sparql = cst.SPARQL_PREFIXES + yaml_raw[yaml_root]["sparql"]
    fB = yaml_raw[yaml_root]["forcedBindings"]
    # forcing bindings available in fB_values
    for binding in fB_values.keys():
        if binding in fB:
            fB[binding]["value"] = fB_values[binding]
    return sparql,fB
    
def diff_JsonQuery(jA,jB,ignore_val=[],show_diff=False,log_message=""):
    """
    Compares json jA towards jB. You can ignore bindings values in 'ignore_val'.
    When 'show_diff' is true, tablaze.py is called for nicer visualization of
    differences.
    'log_message' can be used for verbose notification.
    Returns True or False as comparison result.
    """
    result = True
    diff = []
    for bindingA in jA["results"]["bindings"]:
        found = False
        for bindingB in jB["results"]["bindings"]:
            for key in bindingA:
                ignored = key in ignore_val
                if ((key in bindingB) and (bindingA[key]["type"]==bindingB[key]["type"]) and
                        ((ignored) or ((not ignored) and (bindingA[key]["value"]==bindingB[key]["value"])))):
                    found = True
                else:
                    found = False
                    break
            if found:
                break
        if not found:
            if not show_diff:
                logging.error("{} - Binding\n{}\n not found!".format(log_message,bindingA))
                return False
            else:
                diff.append(bindingA)
                result = False
    if show_diff and len(diff)>0: 
        diff_json = jB
        diff_json["bindings"]=diff
        print("{} Differences".format(log_message))
        tablify(json.dumps(diff_json))
    return result

def compare_queries(i_jA,i_jB,show_diff=False,ignore_val=[]):
    """
    This function compares two json outputs of a SPARQL query.
    jA, jB params are the two json objects containing the results of the query.
    They may also be paths to json files.
    show_diff param, usually false, when set to true will show the entries that
    A has, but not B;
    B has, but not A.
    A boolean is returned, to notify whether jA==jB or not.
    You can ignore the binding value by specifying its name in the ignore_val list. 
    Ignoring the value means that the binding must be there, but that you don't care about its
    actual value.
    """
    # Dealing with paths vs json objects as arguments
    if isinstance(i_jA,str) and os.path.isfile(i_jA):
        with open(i_jA,"r") as fA:
            jA = json.load(fA)
    else:
        jA = i_jA
    if isinstance(i_jB,str) and os.path.isfile(str(i_jB)):
        with open(i_jB,"r") as fB:
            jB = json.load(fB)
    else:
        jB = i_jB
        
    # Checking if every variable in jA is also present in jB and vice versa
    setVarA = set(jA["head"]["vars"])
    setVarB = set(jB["head"]["vars"])
    if setVarA != setVarB:
        for item in (setVarA-setVarB):
            logging.error("A->B Variable '{}'  not found!".format(item))
        for item in (setVarB-setVarA):
            logging.error("B->A Variable '{}'  not found!".format(item))
        return False
            
    # A->B
    # Check if every binding in A exists also in B
    result = diff_JsonQuery(jA,jB,show_diff=show_diff,ignore_val=ignore_val,log_message="A->B")
    # B->A
    result = result and diff_JsonQuery(jB,jA,show_diff=show_diff,ignore_val=ignore_val,log_message="B->A")
    return result

def tablify(json_string):
    # calls tablaze!
    import subprocess
    p = subprocess.Popen(["python","tablaze.py","stdin"],stdin=subprocess.PIPE)
    p.communicate(input=str.encode(json_string))

def query_CompareUpdate(graph,
                        query_path,
                        fBindings,
                        reset,
                        update_path,
                        log_message="",
                        replace={},
                        ignore=[]):
    """
    If reset is true, we perform the query available into 'query_path' to 'graph' with the
    forced bindings in 'fBindings'.
    The sparql obtained is elaborated replacing keys with indexes available in 'replace'.
    We redirect the output of the query towards 'update_path'.
    
    If reset is false, we make the substitution and the query. Then we compare the 
    query output to the file into 'update_path', ignoring the actual value of the 
    bindings in 'ignore' and outputting the message in 'log_message'.
    """
    sparql,fB = get_yaml_data(query_path,fB_values=fBindings)
    for key in replace:
        sparql = sparql.replace(key,replace[key])
    if reset:
        logging.warning("Rebuilding "+update_path)
        return bool(graph.query(sparql,fB=fB,destination=update_path))
    else:
        return query_FileCompare(graph,sparql=sparql,fB=fB,message=log_message,fileAddress=update_path,ignore_val=ignore)


def query_FileCompare(  graph,
                        sparql=cst.SPARQL_QUERY_ALL,
                        fB={},
                        message="query_all",
                        fileAddress=cst.RES_SPARQL_QUERY_ALL,
                        show_diff=False,
                        ignore_val=[]):
    """
    This function performs a 'sparql' query to 'graph', then calls for comparison 
    with the content of 'fileAddress'.
    You can ignore differences in bindings into the 'ignore_val' parameter.
    Then, it notifies the result using the tag contained in 'message' parameter.
    The default behaviour is SELECT * WHERE {?a ?b ?c}.
    'show_diff' parameter will call tablaze.py to print differences to stdout.
    """
    with open(fileAddress,"r") as result:
        template = json.load(result)
    result = graph.query(sparql,fB)
    message = "{} ({} bindings)".format(message,len(result["results"]["bindings"]))
    
    return notify_result(message,compare_queries(template,result,show_diff=show_diff,ignore_val=ignore_val))

def uriFormat(uri):
    return "<"+uri+">" if "//" in uri else uri
