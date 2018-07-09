#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  wotMonitor.py
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
#  This thing is equivalent to the one in insert_thing_2.sparql
#                  _   __  __             _ _             
#   __      _____ | |_|  \/  | ___  _ __ (_) |_ ___  _ __ 
#   \ \ /\ / / _ \| __| |\/| |/ _ \| '_ \| | __/ _ \| '__|
#    \ V  V / (_) | |_| |  | | (_) | | | | | || (_) | |   
#     \_/\_/ \___/ \__|_|  |_|\___/|_| |_|_|\__\___/|_|   
#

import sys
import rlcompleter
import readline
from monitoring import *
from wrap_sepa import Sepa as Engine
from cocktail.Action import Action
from cocktail.Event import Event

commands = ["discover", "describe", "new", "observe", "request", "exit", "back"]
items = ["things", "actions", "events", "properties", "dataschemas", "i-patterns", "exit", "back"]
instances = ["exit","back"]
comps = None

def complete(text, state):
    if text == "":
        matches = comps
    else:
        matches = [x for x in comps if x.startswith(text)]
    if state > len(matches):
        return None
    else:
        return matches[state]
        
def exit_procedure():
    print("Bye bye!")
    sys.exit(0)
        
def item_inspect(sepa,command,method):
    item = input("({})> ".format(command))
    if item == "exit":
        exit_procedure()
    if item != "back":
        if not (item in items):
            print("{}: unknown item!".format(item))
            return []
        else:
            return method(sepa,item,instances)

def main(args):
    global comps
    global instances
    readline.parse_and_bind("tab: complete")
    readline.set_completer(complete)
    
    sepa = Engine()
    
    while True:
        comps = commands
        command = input("> ")
        comps = items
        if not (command in commands):
            print("{}: unknown command!".format(command))
        elif command == "exit":
            exit_procedure()
        elif command == "discover":
            instances = []
            instances += item_inspect(sepa,command,discovery)
        elif command == "describe":
            item_inspect(sepa,command,describe)
        elif command == "new":
            item_inspect(sepa,command,create)
        elif command == "observe":            
            print("Available targets:")
            comps = [x for x in instances if type(x)==Event]
            for event in comps:
                print(event.uri)
            instance = input("(observe)> ")
            if instance == "exit":
                exit_procedure()
            elif instance != "back":
                started_observation = False
                for event in comps:
                    if instance == event.uri:
                        started_observation = observe_event(sepa,event.uri)
                        break
                if not (started_observation):
                    print("{}: unavailable instance!".format(instance))
        elif command == "request":
            actionInstances = [x for x in instances if x["type"]=="Action"]
            comps = actionInstances
            instance = input("(request)> ")
            if not (instance in eventInstances):
                print("{}: unavailable instance!".format(instance))
            else:
                #request_action()
                pass

if __name__ == '__main__':
    sys.exit(main(sys.argv))