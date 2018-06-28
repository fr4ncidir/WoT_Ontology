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

def main(args):
    # builds prefix dictionary
    prefixes = {}
    try:
        with open(args["prefixes"],"r") as prefix_file:
            lines = prefix_file.readlines()
        for line in lines:
            m = re.match(r"prefix ([a-zA-Z]+): <(.+)>",line)
            prefixes[m.groups()[0]] = m.groups()[1]
    except:
        logging.warning("Error while parsing prefixes, skipping...")
    
    # loads the json from a file, or tries from the command line argument
    if os.path.isfile(args["file"]):
        with open(args["file"],"r") as bz_output:
            json_output = json.load(bz_output)
    else:
        json_output = json.loads(input())
    
    # setup the table which will be given in output
    variables = json_output["head"]["vars"]
    pretty = prettytable.PrettyTable(variables)
    
    # fills up the table: one line per binding
    for binding in json_output["results"]["bindings"]:
        tableLine = []
        for v in variables:
            if v in binding:
                nice_value = binding[v]["value"]
                if binding[v]["type"]!="literal":
                    for key in prefixes.keys():
                        # prefix substitution
                        nice_value = nice_value.replace(prefixes[key],key+":")
                tableLine.append("({}) {}".format(binding[v]["type"],nice_value))
            else:
                # special case: absent binding
                tableLine.append("")
        pretty.add_row(tableLine)
    print(str(pretty))
    print("\n{} result(s)".format(len(json_output["results"]["bindings"])))
    return 0

if __name__ == '__main__':
    import sys
    parser = argparse.ArgumentParser(description="Blazegraph query output formatter into nice tables")
    parser.add_argument("file", help="Output in json format to be reformatted: can be a path or the full json or 'stdin'")
    parser.add_argument("-prefixes", default="./prefixes.txt", help="Optional file containing prefixes to be replaced into the table")
    args = vars(parser.parse_args())
    sys.exit(main(args))