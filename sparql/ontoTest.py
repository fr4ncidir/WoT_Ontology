#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  ontoTest.py
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

import argparse
import requests
import blazegraph as bz
import os
import logging

logging.basicConfig(format='%(levelname)s %(asctime)-15s %(message)s',level=logging.INFO)   

def main(args):
    # Deleting everything
    r = bz.update_blazegraph(args,"delete where {?a ?b ?c}")
    assert r.status_code == 200
    logging.info("Deleted everything from Blazegraph")
    
    # Adding test webthings
    r = bz.update_blazegraph(args,bz.file_to_string("./setups/insert_thing_1.sparql"))
    assert r.status_code == 200
    r = bz.update_blazegraph(args,bz.file_to_string("./setups/insert_thing_2.sparql"))
    assert r.status_code == 200
    logging.info("Inserted two test things")
    
    # Performing base queries and saving result
    print("Building test result files...")
    bz.query_and_write("select * where {?a ?b ?c}","queries",forceName="query_all")
    for fileName in list(filter(lambda myfile: not (myfile.startswith(".") or os.path.isdir("./queries/"+myfile)),os.listdir("./queries"))):
        query_and_write("./queries/{}".format(fileName),"queries")
        
    
    
    return 0

if __name__ == '__main__':
    import sys
    parser = argparse.ArgumentParser(description="WoT ontology test suite")
    parser.add_argument("-ip", default="localhost", help="Blazegraph ip")
    parser.add_argument("-port", default=9999, help="Blazegraph port")
    args = vars(parser.parse_args())
    sys.exit(main(args))
