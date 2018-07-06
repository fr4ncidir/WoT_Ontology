#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  tablaze.py
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

import argparse
import prettytable
import json
import re
import os
import logging

logging.basicConfig(format="%(levelname)s %(asctime)-15s - %s(filename)s - %(message)s",level=logging.INFO)

def tablify(json_string):
    # calls tablaze!
    import subprocess
    p = subprocess.Popen(["python3","tablaze.py","stdin"],stdin=subprocess.PIPE)
    p.communicate(input=str.encode(json_string))

def cfr_bindings(bA,bB,ignorance):
    for key in bA:
        if ((not (key in bB)) or ((bA[key]["type"] != bB[key]["type"]) or 
            ((not (key in ignorance)) and (bA[key]["value"] != bB[key]["value"])))):
            return False
    return True

def diff_JsonQuery(jA,jB,show_diff=True,ignore_val=[],log_message=""):
    result = True
    diff = []
    
    for bindingA in jA["results"]["bindings"]:
        eq_binding = False
        for bindingB in jB["results"]["bindings"]:
            eq_binding = cfr_bindings(bindingA,bindingB,ignore_val)
            if eq_binding:
                break
        if not eq_binding:
            diff.append(bindingA)
            result = False
    if show_diff and len(diff)>0: 
        jdiff=json.loads('{"head": {"vars": ["a", "b", "c"]}}')
        jdiff["results"]={}
        jdiff["results"]["bindings"] = diff
        print("{} Differences".format(log_message))
        tablify(json.dumps(jdiff))
    return result

def compare_queries(i_jA,i_jB,show_diff=True):
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
    setVarA = set(jA["head"]["vars"])
    setVarB = set(jB["head"]["vars"])
    if setVarA != setVarB:
        for item in (setVarA-setVarB):
            logging.error("A->B Variable '{}'  not found!".format(item))
        for item in (setVarB-setVarA):
            logging.error("B->A Variable '{}'  not found!".format(item))
        return False
        
    result = diff_JsonQuery(jA,jB,show_diff=show_diff,log_message="A->B")
    # B->A
    result = result and diff_JsonQuery(jB,jA,show_diff=show_diff,log_message="B->A")
    return result

def main(args):
    print(compare_queries("./missing.txt","./res_thing1.txt",show_diff=True))
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
