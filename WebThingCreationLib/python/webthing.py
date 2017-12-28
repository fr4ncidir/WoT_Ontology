#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  webthing.py
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

from sepy import JSAPObject,LowLevelKP
from uuid import uuid4
import logging

logging.basicConfig(format="%(levelname)s %(asctime)-15s %(message)s",level=logging.DEBUG)
logger = logging.getLogger("sepaLogger")

class WebThing:
	"WebThing class object, as defined by in WoT Arces research group"
	instances = 0
	
	def __init__(self, jsap_path, name="WT{}".format(instances), uri=str(uuid4())):
		self.jsap_path = jsap_path
		self.name = name
		self.uri = uri
		self.__properties = [] 		# list of Property
		self.__actions = [] 		# list of Action
		self.__events = []			# list of Event
		self.__sub_things = []		# list of WebThing
		self.__forProperties = [] 	# list of pairs (Action | Event,Property)
		WebThing.instances += 1
		
	def add_property(self,newproperty):
		if not isinstance(newproperty,Property):
			raise TypeError
		self.__properties.append(newproperty)
		logger.debug("Added Property {}({})".format(newproperty.getName(),newproperty.getUri()))
		return len(self.__properties)
		
	def add_action(self,newaction):
		if not isinstance(newaction,Action):
			raise TypeError
		self.__actions.append(newaction)
		logger.debug("Added Action {}({})".format(newaction.getName(),newAction.getUri()))
		return len(self.__actions)
		
	def add_event(self,newevent):
		if not isinstance(newevent,Event):
			raise TypeError
		self.__events.append(newevent)
		logger.debug("Added Event {}({})".format(newevent.getName(),newevent.getUri()))
		return len(self.__events)
	
	def add_sub_thing(self,subthing):
		if not isinstance(subthing,WebThing):
			raise TypeError
		self.__sub_things.append(subthing)
		logger.debug("Added SubThing {}({})".format(subthing.getName(),subthing.getUri()))
		return len(self.__sub_things)
		
	def add_forProperty(self,origin,destination):
		if not ((isinstance(origin,Action) or isinstance(origin,Event)) and (isinstance(destination,Property))):
			raise TypeError
		self.__forProperties.append((origin,destination))
		logger.debug("Added forProperty connection between {}({}) and {}({})".format(origin.getName(),origin.getUri(),destination.getName(),destination.getUri()))
		return len(self.__forProperties)
		
	def getName(self):
		return self.name
		
	def getUri(self):
		return self.uri
		
	def getForcedBindings(self):
		return {"thing" : self.uri,"name" : self.name }
	
	def post(self,jpar_path,secure=False):
		kp = LowLevelKP.LowLevelKP(jpar_path,self.jsap_path,10)
		
		# first step: declare the thing
		sparql = kp.jsapHandler.getUpdate("ADD_NEW_THING",self.getForcedBindings())
		kp.update(sparql,secure)
		
		# second step: add properties
		for item in self.__properties:
			sparql = kp.jsapHandler.getUpdate("ADD_PROPERTY",item.getForcedBindings())
			kp.update(sparql,secure)
		
		# third step: add events
		for item in self.__events:
			if item.isPropertyChangedEvent():
				update = "ADD_PROPERTY_CHANGED_EVENT"
			else:
				update = "ADD_EVENT"
			sparql = kp.jsapHandler.getUpdate(update,item.getForcedBindings())
			kp.update(sparql,secure)
		
		# fourth step: add actions
		for item in self.__actions:
			sparql = kp.jsapHandler.getUpdate("ADD_NEW_ACTION",item.getForcedBindings())
			kp.update(sparql,secure)
		
		# fifth step: include forProperties
		for item in self.__forProperties:
			sparql = kp.jsapHandler.getUpdate("ADD_FORPROPERTY",{"item" : item[0],"property" : item[1]})
			kp.update(sparql,secure)
		
		# sixth step: include subThings
		for item in self.__sub_things:
			sparql = kp.jsapHandler.getUpdate("ADD_NESTED_THING",{"thingFather" : self.uri,"thing" : item.getUri()})
			kp.update(sparql,secure)
			
		
		
class Action:
	"Action class object, as defined by in WoT Arces research group"
	instances = 0
	
	def __init__(self,thing,name="Action{}".format(instances),uri=str(uuid4()),in_dataschema="",out_dataschema=""):
		self.thing = thing
		self.name = name
		self.uri = uri
		self.in_dataschema = in_dataschema
		self.out_dataschema = out_dataschema
		
	def getForcedBindings(self):
		forcedBindings = {
			"thing" : self.thing,
			"aName" : self.name,
			"action" : self.uri }
		
		if self.in_dataschema!="":
			forcedBindings["newInDataSchema"] = self.in_dataschema
		if self.out_dataschema!="":
			forcedBindings["newOutDataSchema"] = self.out_dataschema
		return forcedBindings
			
	def getName(self):
		return self.name
		
	def getUri(self):
		return self.uri

class Event:
	"Event class object, as defined by in WoT Arces research group"
	instances = 0
	
	def __init__(self,thing,name="Event{}".format(instances),uri=str(uuid4),out_dataschema="",PCFlag=False):
		self.thing = thing
		self.name = name
		self.uri = uri
		self.out_dataschema = out_dataschema
		self.pc_flag = PCFlag
		
	def isPropertyChangedEvent():
		return self.pc_flag
		
	def getForcedBindings(self):
		forcedBindings = {
			"thing" : self.thing,
			"eName" : self.name,
			"event" : self.uri }
		
		if self.out_dataschema!="" and self.pc_flag==False:
			forcedBindings["outDataSchema"] = self.out_dataschema	
		return forcedBindings
	
class Property:
	"Property class object, as defined by in WoT Arces research group"
	instances = 0
	
	def __init__(self,thing,name="Property{}".format(instances),uri=str(uuid4),dataschema="",writable=True,stability=0,value=""):
		self.thing = thing
		self.name = name
		self.uri = uri
		self.dataschema = dataschema
		self.writable = writable
		self.stability = stability
		self.value = value
		
	def getForcedBindings(self):
		return {
			"thing" : self.thing,
			"newName" : self.name,
			"property" : self.uri,
			"newDataSchema" : self.dataschema,
			"newWritable" : self.writable,
			"newStability" : self.stability,
			"newValue" : self.value }
			
	def getName(self):
		return self.name
		
	def getUri(self):
		return self.uri
		
	


if __name__ == '__main__':
	import sys
	TD = "C:/Users/Francesco/Documents/Work/WoT_Ontology/thing_description.jsap"
	JPAR = "C:/Users/Francesco/Desktop/constance/constance.jpar"
	wt = WebThing(TD,"mything","wot:mything")
	wt.post(JPAR)
	sys.exit(1)
