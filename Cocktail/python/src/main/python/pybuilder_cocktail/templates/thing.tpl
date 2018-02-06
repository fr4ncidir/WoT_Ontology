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

wt = WebThing(JSAP,name="{{thing.name}}",uri="{{thing.uri}}")
{% for name in thing.properties %}
{{name}} = Property(wt,"{{name}}",uri="wot:{{name}}",dataschema="{{thing.properties[name].dataschema}}",writable={{thing.properties[name].writable}},value={{thing.properties[name].value}})
{%- endfor %}
{% for name in thing.actions %}
{{name}} = Action(wt,name="{{name}}",uri="wot:{{name}}")
{%- endfor %}

{% for name in thing.actions %}
def {{name}}_executor():
  print("{{name}}")

{%- endfor %}

if __name__ == '__main__':
  import sys

  {% for name in thing.properties %}
  wt.add_property({{name}})
  {%- endfor %}
  {% for name in thing.actions %}
  wt.add_action({{name}})
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
      {% for name in thing.actions %}
      if item["action"]["value"]=="{}{}".format(WOT,"{{name}}"):
        {{name}}_executor()
        continue
      {%- endfor %}
      pass
