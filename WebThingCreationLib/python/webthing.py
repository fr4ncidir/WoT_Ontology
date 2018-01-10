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

logging.basicConfig(format="%(filename)s-%(funcName)s-%(levelname)s %(asctime)-15s %(message)s",level=logging.INFO)
logger = logging.getLogger("sepaLogger")

class WebThing:
	"WebThing class object, as defined by in WoT Arces research group"
	instances = 0
	
	def __init__(self, jsap_path, jpar_path, name="WT{}".format(instances), uri=str(uuid4())):
		self.jsap_path = jsap_path
		self.jpar_path = jpar_path
		self.name = name
		self.uri = uri
		self.__properties = [] 		# list of Property
		self.__actions = [] 		# list of Action
		self.__events = []			# list of Event
		self.__sub_things = []		# list of WebThing
		self.__forProperties = [] 	# list of pairs (Action | Event,Property)
		self.kp = LowLevelKP.LowLevelKP(self.jpar_path,self.jsap_path,10)
		WebThing.instances += 1
		
	def add_property(self,newproperty):
		if not isinstance(newproperty,Property):
			raise TypeError
		self.__properties.append(newproperty)
		logger.info("Added Property {}({})".format(newproperty.getName(),newproperty.getUri()))
		return len(self.__properties)
		
	def add_action(self,newaction):
		if not isinstance(newaction,Action):
			raise TypeError
		self.__actions.append(newaction)
		logger.info("Added Action {}({})".format(newaction.getName(),newaction.getUri()))
		return len(self.__actions)
		
	def add_event(self,newevent):
		if not isinstance(newevent,Event):
			raise TypeError
		self.__events.append(newevent)
		logger.info("Added Event {}({})".format(newevent.getName(),newevent.getUri()))
		return len(self.__events)
	
	def add_sub_thing(self,subthing):
		if not isinstance(subthing,WebThing):
			raise TypeError
		self.__sub_things.append(subthing)
		logger.info("Added SubThing {}({})".format(subthing.getName(),subthing.getUri()))
		return len(self.__sub_things)
		
	def add_forProperty(self,origin,destination):
		if not ((isinstance(origin,Action) or isinstance(origin,Event)) and (isinstance(destination,Property))):
			raise TypeError
		self.__forProperties.append((origin,destination))
		logger.info("Added forProperty connection between {}({}) and {}({})".format(origin.getName(),origin.getUri(),destination.getName(),destination.getUri()))
		return len(self.__forProperties)
		
	def getName(self):
		return self.name
		
	def getUri(self):
		return self.uri
		
	def getKP(self):
		return self.kp
		
	def getForcedBindings(self):
		return {"thing" : self.uri,"name" : self.name }
	
	def post(self,secure=False):
		# first step: declare the thing
		logger.info("Calling ADD_NEW_THING for {}({})".format(self.name,self.uri))
		sparql = self.kp.jsapHandler.getUpdate("ADD_NEW_THING",self.getForcedBindings())
		self.kp.update(sparql,secure)
		
		# second step: add properties
		for item in self.__properties:
			logger.info("Adding property {}({}) to {}({})".format(item.getName(),item.getUri(),self.name,self.uri))
			sparql = self.kp.jsapHandler.getUpdate("ADD_PROPERTY",item.getForcedBindings())
			self.kp.update(sparql,secure)
		
		# third step: add events
		for item in self.__events:
			if item.isPropertyChangedEvent():
				update = "ADD_PROPERTY_CHANGED_EVENT"
			else:
				update = "ADD_EVENT"
			logger.info("Adding event {}({}) to {}({})".format(item.getName(),item.getUri(),self.name,self.uri))
			sparql = self.kp.jsapHandler.getUpdate(update,item.getForcedBindings())
			self.kp.update(sparql,secure)
		
		# fourth step: add actions
		for item in self.__actions:
			logger.info("Adding action {}({}) to {}({})".format(item.getName(),item.getUri(),self.name,self.uri))
			sparql = self.kp.jsapHandler.getUpdate("ADD_NEW_ACTION",item.getForcedBindings())
			self.kp.update(sparql,secure)
		
		# fifth step: include forProperties
		for (origin,destination) in self.__forProperties:
			logger.info("Connecting {}-{}({}) to Property {}({})".format(type(origin).__name__,origin.getName(),origin.getUri(),destination.getName(),destination.getUri()))
			sparql = self.kp.jsapHandler.getUpdate("ADD_FORPROPERTY",{"item" : origin.getUri(),"property" : destination.getUri()})
			self.kp.update(sparql,secure)
		
		# sixth step: include subThings
		for item in self.__sub_things:
			logger.info("Nesting {}({}) into {}({})".format(item.getName(),item.getUri(),self.name,self.uri))
			sparql = self.kp.jsapHandler.getUpdate("ADD_NESTED_THING",{"thingFather" : self.uri,"thing" : item.getUri()})
			self.kp.update(sparql,secure)
			
	def listenForActionRequests(self,handler,secure=False):
		logger.info("Subscribing to Action requests for WebThing {}".format(self.uri))
		sparql = self.kp.jsapHandler.getQuery("GET_ACTION_REQUEST",{"thing" : self.uri})
		spuid = self.kp.subscribe(sparql, "ActionRequest_{}_Notification".format(self.uri), handler, secure)
		return (self.kp,spuid)
					
	@staticmethod
	def discoveryThings(jpar,jsap,secure=False):
		kp = LowLevelKP.LowLevelKP(jpar,jsap,10)
		sparql = kp.jsapHandler.getQuery("ALL_THINGS",{})
		status,results = kp.query(sparql,secure)
		return results["results"]["bindings"]
		
class DefaultActionCompletionHandler:
		def __init__(self,kp,secure):
			self.kp = kp
			self.secure = secure
		def setSubID(self,subid):
			self.subid = subid
		def handle(self, added, removed):
			for item in added:
				logger.info("DefaultActionCompletionHandler: {} timestamp received".format(item["timestamp"]["value"]))
				try:
					logger.info("DefaultActionCompletionHandler: {} output received".format(item["value"]["value"]))
				except Exception:
					pass
			self.kp.unsubscribe(self.subid,self.secure)
	
class Action:
	"Action class object, as defined by in WoT Arces research group"
	instances = 0

	def __init__(self,thing,name="Action{}".format(instances),uri=str(uuid4()),in_dataschema="",out_dataschema=""):
		self.thing = thing
		self.name = name
		self.uri = uri
		self.in_dataschema = in_dataschema
		self.out_dataschema = out_dataschema
		Action.instances += 1
		
	def getForcedBindings(self):
		forcedBindings = {
			"thing" : self.thing.getUri(),
			"newName" : self.name,
			"action" : self.uri,
			"newInDataSchema" : self.in_dataschema,
			"newOutDataSchema" : self.out_dataschema }
		return forcedBindings
			
	def getName(self):
		return self.name
		
	def getUri(self):
		return self.uri
	
	@staticmethod
	def askForAction(jpar,jsap,thingUri,actionUri,instanceUri="wot:"+str(uuid4()),input_value=None,output_handler=None,secure=False):
		kp = LowLevelKP.LowLevelKP(jpar,jsap,10)
		logger.info("Subscribing to instance {} of Action {} completion and output (WebThing {})".format(instanceUri,actionUri,thingUri))
		sparql = kp.jsapHandler.getQuery("GET_ACTION_COMPLETION_AND_OUTPUT",{"thing" : thingUri,"action" : actionUri,"instance" : instanceUri})
		if output_handler is None:
			output_handler = DefaultActionCompletionHandler(kp,secure)
		spuid = kp.subscribe(sparql, "CompletionOutput_{}_Notification".format(instanceUri), output_handler, secure)
		output_handler.setSubID(spuid)
		if input_value is None:
			logger.info("Requesting instance {} for Action {} (WebThing {}) - no input given".format(instanceUri,actionUri,thingUri))
			sparql = kp.jsapHandler.getUpdate("POST_ACTION_INSTANCE_NO_INPUT",{"action" : actionUri,"instance" : instanceUri})
		else:
			logger.info("Requesting instance {} for Action {} (WebThing {}) - input: {}".format(instanceUri,actionUri,thingUri,input_value))
			sparql = kp.jsapHandler.getUpdate("POST_ACTION_INSTANCE_WITH_INPUT",{"action" : actionUri,"instance" : instanceUri,"value" : input_value})
		kp.update(sparql,secure)
		return instanceUri
			
	@staticmethod
	def waitActionConfirmation(jpar,jsap,instanceUri,handler,secure=False):
		kp = LowLevelKP.LowLevelKP(jpar,jsap,10)
		logger.info("Subscribing to confirmation timestamp for ActionInstance {}".format(instanceUri))
		sparql = kp.jsapHandler.getQuery("GET_CONFIRMATION_TIMESTAMP",{"instance" : instanceUri})
		return (kp,kp.subscribe(sparql, "ActionConfirmation_{}_Notification".format(instanceUri), handler, secure))
		
	def postActionConfirmation(self,instanceUri,secure=False):
		logger.info("Posting confirmation for {} Action {} (WebThing {})".format(instanceUri,self.uri,self.thing.getUri()))
		sparql = self.thing.getKP().jsapHandler.getUpdate("ADD_CONFIRMATION_TIMESTAMP",{"instance" : instanceUri})
		self.thing.getKP().update(sparql,secure)
		
	def postActionCompletion(self,instanceUri,output_value=None,secure=False):
		if output_value is None:
			logger.info("Posting completion for {} Action {} (WebThing {}) - no output given".format(instanceUri,self.uri,self.thing.getUri()))
			sparql = self.thing.getKP().jsapHandler.getUpdate("ADD_COMPLETION_TIMESTAMP_NO_OUTPUT",{"instance" : instanceUri})
		else:
			logger.info("Posting completion for {} Action {} (WebThing {}) - output: {}".format(instanceUri,self.uri,self.thing.getUri(),output_value))
			sparql = self.thing.getKP().jsapHandler.getUpdate("ADD_COMPLETION_TIMESTAMP_WITH_OUTPUT",{"instance" : instanceUri,"value" : output_value})
		self.thing.getKP().update(sparql,secure)
		
	@staticmethod
	def getActionList(jpar,jsap,thingUri=None,secure=False):
		kp = LowLevelKP.LowLevelKP(jpar,jsap,10)
		if thingUri is None:
			sparql = kp.jsapHandler.getQuery("LIST_ACTIONS",{})
		else:
			sparql = kp.jsapHandler.getQuery("LIST_ACTIONS",{"thing" : thingUri})
		status,results = kp.query(sparql,secure)
		return results["results"]["bindings"]
		

class Event:
	"Event class object, as defined by in WoT Arces research group"
	instances = 0
	
	def __init__(self,thing,name="Event{}".format(instances),uri=str(uuid4()),out_dataschema="",PCFlag=False):
		self.thing = thing
		self.name = name
		self.uri = uri
		self.out_dataschema = out_dataschema
		self.pc_flag = PCFlag
		Event.instances += 1
		
	def isPropertyChangedEvent(self):
		return self.pc_flag
		
	def getForcedBindings(self):
		forcedBindings = {
			"thing" : self.thing.getUri(),
			"eName" : self.name,
			"event" : self.uri }
		
		if self.out_dataschema!="" and self.pc_flag==False:
			forcedBindings["outDataSchema"] = self.out_dataschema	
		return forcedBindings
		
	def getName(self):
		return self.name
		
	def getUri(self):
		return self.uri
		
	def throwNewEvent(self,output_value=None,secure=False):
		if output_value is None:
			logger.info("Throwing new event instance (autogen URI) for Event {} (WebThing {}) - no output given".format(self.uri,self.thing.getUri()))
			sparql = self.thing.getKP().jsapHandler.getUpdate("POST_NEW_EVENT_WITHOUT_OUTPUT",{"event" : self.uri,"thing" : self.thing.getUri()})
		else:
			logger.info("Throwing new event instance (autogen URI) for Event {} (WebThing {}) - output: {}".format(self.uri,self.thing.getUri(),output_value))
			sparql = self.thing.getKP().jsapHandler.getUpdate("POST_NEW_EVENT_WITH_OUTPUT",{"event" : self.uri,"thing" : self.thing.getUri(), "newDataValue" : output_value})
		self.thing.getKP().update(sparql,secure)
		
	@staticmethod
	def subscribeToEvent(jpar,jsap,thingUri,eventUri,handler,secure=False):
		kp = LowLevelKP.LowLevelKP(jpar,jsap,10)
		logger.info("Subscribing to event {} (WebThing {})".format(eventUri,thingUri))
		sparql = self.kp.jsapHandler.getQuery("GET_EVENT_NOTIFICATION",{"thing" : thingUri,"event" : eventUri})
		kp.subscribe(sparql, "Event_{}_Notification".format(eventUri), handler, secure)
		
	@staticmethod
	def getEventList(jpar,jsap,thingUri=None,secure=False):
		kp = LowLevelKP.LowLevelKP(jpar,jsap,10)
		if thingUri is None:
			sparql = kp.jsapHandler.getQuery("LIST_EVENTS",{})
		else:
			sparql = kp.jsapHandler.getQuery("LIST_EVENTS",{"thing" : thingUri})
		status,results = kp.query(sparql,secure)
		return results["results"]["bindings"]
	
class Property:
	"Property class object, as defined by in WoT Arces research group"
	instances = 0
	
	def __init__(self,thing,name="Property{}".format(instances),uri=str(uuid4()),dataschema="",writable=True,stability=0,value=""):
		self.thing = thing.getUri()
		self.name = name
		self.uri = uri
		self.dataschema = dataschema
		self.writable = writable
		self.stability = stability
		self.value = value
		Property.instances += 1
		
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
		
	@staticmethod
	def subscribeToValueChange(propertyUri,handler,secure=False):
		kp = LowLevelKP.LowLevelKP(jpar,jsap,10)
		logger.info("Subscribing to property {} value change".format(propertyUri))
		sparql = self.kp.jsapHandler.getQuery("GET_EVENT_NOTIFICATION",{"thing" : thingUri,"event" : eventUri})
		return (kp,kp.subscribe(sparql, "Property_{}_value_subscription".format(propertyUri), handler, secure))
		
	@staticmethod
	def getPropertyList(jpar,jsap,thingUri=None,secure=False):
		kp = LowLevelKP.LowLevelKP(jpar,jsap,10)
		if thingUri is None:
			sparql = kp.jsapHandler.getQuery("LIST_PROPERTIES",{})
		else:
			sparql = kp.jsapHandler.getQuery("LIST_PROPERTIES",{"thing" : thingUri})
		status,results = kp.query(sparql,secure)
		return results["results"]["bindings"]
