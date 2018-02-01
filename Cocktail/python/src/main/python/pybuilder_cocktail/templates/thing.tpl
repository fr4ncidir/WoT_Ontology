#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  {{thing.name}}.py
#
#  Copyright 2017 Francesco Antoniazzi <francesco.antoniazzi@unibo.it>
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

import colorama
from colorama import Fore, Style
import logging
from wot_init import *
from webthing import *

logging.basicConfig(format=LOGFORMAT,level=LOGLEVEL)

WOT = "http://wot.arces.unibo.it/sepa#"
ACCENDI_RISCALDAMENTO = "AccendiRiscaldamento"
SPEGNI_RISCALDAMENTO = "SpegniRiscaldamento"

wt = WebThing(JSAP,name="{{thing.name}}",uri="{{thing.uri}}")
{% for property in thing.properties %}
{{property.name}} = Property(wt,"{{property.name}}",uri="wot:{{property.name}}",dataschema="{{property.dataschema}}",writable={{property.writable}},value={{property.value}})
{%- endfor %}
{% for action in thing.actions %}
{{action.name}} = Action(wt,name="{{action.name}}",uri="wot:{{action.name}}")
{%- endfor %}

{% for action in thing.actions %}
def {{action.name}}_executor():
print("{{action.name}}")

{%- endfor %}

if __name__ == '__main__':
import sys

{% for property in thing.properties %}
wt.add_property({{property.name}})
{%- endfor %}
{% for action in thing.actions %}
wt.add_action({{action.name}})
{%- endfor %}

{% for forP in thing.for_properties %}
wt.add_forProperty({{forP[0].name}},{{forP[1].name}})
{%- endfor %}

wt.post()

kp,subid = wt.listenForActionRequests(ActionRequestHandler())

colorama.init()
print(Fore.RED + "Waiting for action requests..." + Style.RESET_ALL)

while True:
  try:
    pass
  except KeyboardInterrupt:
    print("CTRL-C pressed! Bye!")
    kp.unsubscribe(subid,False)
    sys.exit(0)

class ActionRequestHandler:
def __init__(self):
  pass
def handle(self, added, removed):
  for item in added:
    {% for action in thing.actions %}
    if item["action"]["value"]=="{}{}".format(WOT,"{{action.name}}"):
      {{action.name}}_executor()
      continue
    {%- endfor %}
