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

from copy import deepcopy
from sepy import JSAPObject,LowLevelKP
from uuid import uuid4
from itertools import count
import logging

logging.basicConfig(format="%(filename)s-%(funcName)s-%(levelname)s %(asctime)-15s %(message)s",level=logging.INFO)
logger = logging.getLogger("sepaLogger")

class WebThing:
	"WebThing class object, as defined by in WoT Arces research group"
	instances = count(1)

	def __init__(self, jsap_path=None, name="WT{}".format(instances), uri=str(uuid4())):
		if jsap_path is None:
			self.jsap_obj = None
		else:
			self.jsap_obj = JSAPObject.JSAPObject(jsap_path)
		self._name = name
		self._uri = uri
		self.__properties = {} 		# dict name:property
		self.__actions = {} 		# dict name:action
		self.__events = {}			# dict name:event
		self.__sub_things = []		# list of WebThing
		self.__forProperties = [] 	# list of pairs (Action | Event,Property)
		self.kp = LowLevelKP.LowLevelKP()
		next(WebThing.instances)

	def add_property(self,newproperty):
		if not isinstance(newproperty,Property):
			raise TypeError
		if newproperty.name in self.__properties:
			raise ValueError("%s already defined" % newproperty.name)
		self.__properties[newproperty.name] = newproperty
		logger.info("Added Property {}({})".format(newproperty.name,newproperty.uri))
		newproperty.setThing(self)
		return len(self.__properties)

	def add_action(self,newaction):
		if not isinstance(newaction,Action):
			raise TypeError
		if newaction.name in self.__actions:
			raise ValueError("%s already defined" % newaction.name)
		self.__actions[newaction.name] = newaction
		logger.info("Added Action {}({})".format(newaction.name,newaction.uri))
		newaction.setThing(self)
		return len(self.__actions)

	def add_event(self,newevent):
		if not isinstance(newevent,Event):
			raise TypeError
		if newevent.name in self.__events:
			raise ValueError("%s already defined" % newevent.name)
		self.__events[newevent.name]= newevent
		logger.info("Added Event {}({})".format(newevent.name,newevent.uri))
		newevent.setThing(self)
		return len(self.__events)

	def add_sub_thing(self,subthing):
		if not isinstance(subthing,WebThing):
			raise TypeError
		self.__sub_things.append(subthing)
		logger.info("Added SubThing {}({})".format(subthing.name,subthing.uri))
		return len(self.__sub_things)

	def add_forProperty(self,origin,destination):
		if not ((isinstance(origin,Action) or isinstance(origin,Event)) and (isinstance(destination,Property))):
			raise TypeError
		self.__forProperties.append((origin,destination))
		logger.info("Added forProperty connection between {}({}) and {}({})".format(origin.name,origin.uri,destination.name,destination.uri))
		return len(self.__forProperties)

	@property
	def properties(self):
		return deepcopy(self.__properties)

	@property
	def actions(self):
		return deepcopy(self.__actions)

	@property
	def events(self):
		return deepcopy(self.__events)

	@property
	def name(self):
		return self._name

	@property
	def uri(self):
		return self._uri

	def getJSAPObject(self):
		return self.jsap_obj

	def getKP(self):
		return self.kp

	def getForcedBindings(self):
		return {"thing" : self.uri,"name" : self.name }

	def setJSAP(self,jsap_path):
		self.jsap_obj = JSAPObject.JSAPObject(jsap_path)

	def post(self):
		if self.jsap_obj is None:
			raise ValueError
		# first step: declare the thing
		logger.info("Calling ADD_NEW_THING for {}({})".format(self.name,self.uri))
		sparql = self.jsap_obj.getUpdate("ADD_NEW_THING",self.getForcedBindings())
		self.kp.update(self.jsap_obj.updateUri,sparql)

		# second step: add properties
		for item in self.__properties:
			logger.info("Adding property {}({}) to {}({})".format(self.__properties[item].name,self.__properties[item].uri,self.name,self.uri))
			sparql =  self.jsap_obj.getUpdate("ADD_PROPERTY",self.__properties[item].getForcedBindings())
			self.kp.update(self.jsap_obj.updateUri,sparql)

		# third step: add events
		for item in self.__events:
			if self.__events[item].isPropertyChangedEvent():
				update = "ADD_PROPERTY_CHANGED_EVENT"
			else:
				update = "ADD_EVENT"
			logger.info("Adding event {}({}) to {}({})".format(self.__events[item].name,self.__events[item].uri,self.name,self.uri))
			sparql =  self.jsap_obj.getUpdate(update,self.__events[item].getForcedBindings())
			self.kp.update(self.jsap_obj.updateUri,sparql)

		# fourth step: add actions
		for item in self.__actions:
			logger.info("Adding action {}({}) to {}({})".format(self.__actions[item].name,self.__actions[item].uri,self.name,self.uri))
			sparql =  self.jsap_obj.getUpdate("ADD_NEW_ACTION",self.__actions[item].getForcedBindings())
			self.kp.update(self.jsap_obj.updateUri,sparql)

		# fifth step: include forProperties
		for (origin,destination) in self.__forProperties:
			logger.info("Connecting {}-{}({}) to Property {}({})".format(type(origin).__name__,origin.name,origin.uri,destination.name,destination.uri))
			sparql =  self.jsap_obj.getUpdate("ADD_FORPROPERTY",{"item" : origin.uri,"property" : destination.uri})
			self.kp.update(self.jsap_obj.updateUri,sparql)

		# sixth step: include subThings
		for item in self.__sub_things:
			logger.info("Nesting {}({}) into {}({})".format(item.name,item.uri,self.name,self.uri))
			sparql =  self.jsap_obj.getUpdate("ADD_NESTED_THING",{"thingFather" : self.uri,"thing" : item.uri})
			self.kp.update(self.jsap_obj.updateUri,sparql)

	def listenForActionRequests(self,handler):
		logger.info("Subscribing to Action requests for WebThing {}".format(self.uri))
		sparql =  self.jsap_obj.getQuery("GET_ACTION_REQUEST",{"thing" : self.uri})
		subid = self.kp.subscribe(self.jsap_obj.subscribeUri,sparql, "ActionRequest_{}_Notification".format(self.uri), handler)
		return (self.kp,subid)
	
	def throwNewEvent(self,eventName,output_value=None):
		if output_value is None:
			logger.info("Throwing new event instance (autogen URI) for Event {} (WebThing {}) - no output given".format(self.events[eventName],self.name))
			sparql = self.jsap_obj.getUpdate("POST_NEW_EVENT_WITHOUT_OUTPUT",{"event" : self.__events[eventName].uri,"thing" : self.uri})
		else:
			logger.info("Throwing new event instance (autogen URI) for Event {} (WebThing {}) - output: {}".format(self.events[eventName],self.uri,output_value))
			sparql = self.jsap_obj.getUpdate("POST_NEW_EVENT_WITH_OUTPUT",{"event" : self.__events[eventName].uri,"thing" : self.uri, "newDataValue" : output_value})
		self.kp.update(self.jsap_obj.updateUri,sparql)

	@staticmethod
	def discoveryThings(jsap_obj):
		kp = LowLevelKP.LowLevelKP()
		sparql = jsap_obj.getQuery("ALL_THINGS",{})
		status,results = kp.query(jsap_obj.queryUri,sparql)
		return results["results"]["bindings"]
		
	def postActionConfirmation(self,action,instanceUri,secure=False):
		if not action.name in self.__actions:
			raise ValueError("WebThing {} doesn't contain {}".format(self.name,action.name))
		logger.info("Posting confirmation for {} Action {} (WebThing {})".format(instanceUri,action.uri,self.uri))
		sparql = self.getJSAPObject().getUpdate("ADD_CONFIRMATION_TIMESTAMP",{"instance" : instanceUri})
		self.getKP().update(self.getJSAPObject().updateUri,sparql)

	def postActionCompletion(self,action,instanceUri,output_value=None):
		if not action.name in self.__actions:
			raise ValueError("WebThing {} doesn't contain {}".format(self.name,action.name))
		if output_value is None:
			logger.info("Posting completion for {} Action {} (WebThing {}) - no output given".format(instanceUri,action.uri,self.uri))
			sparql = self.getJSAPObject().getUpdate("ADD_COMPLETION_TIMESTAMP_NO_OUTPUT",{"instance" : instanceUri})
		else:
			logger.info("Posting completion for {} Action {} (WebThing {}) - output: {}".format(instanceUri,action.uri,self.uri,output_value))
			sparql = self.getJSAPObject().getUpdate("ADD_COMPLETION_TIMESTAMP_WITH_OUTPUT",{"instance" : instanceUri,"value" : output_value})
		self.getKP().update(self.getJSAPObject().updateUri,sparql)

class DefaultActionCompletionHandler:
		def __init__(self,kp,secure=False):
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
	instances = count(1)

	def __init__(self,name="Action{}".format(instances),uri=str(uuid4()),in_dataschema="",out_dataschema=""):
		self.thing = None
		self._name = name
		self._uri = uri
		self.in_dataschema = in_dataschema
		self.out_dataschema = out_dataschema
		next(Action.instances)

	def getForcedBindings(self):
		if self.thing is None:
			raise ValueError("Undefined container WebThing for {}".format(self._name))
		forcedBindings = {
			"thing" : self.thing,
			"newName" : self._name,
			"action" : self._uri,
			"newInDataSchema" : self.in_dataschema,
			"newOutDataSchema" : self.out_dataschema }
		return forcedBindings
	
	def setThing(self,thing):
		self.thing = thing.uri
	
	@property
	def name(self):
		return self._name

	@property
	def uri(self):
		return self._uri

	@staticmethod
	def askForAction(jsap_obj,thingUri,actionUri,instanceUri="wot:"+str(uuid4()),input_value=None,output_handler=None):
		kp = LowLevelKP.LowLevelKP()
		logger.info("Subscribing to instance {} of Action {} completion and output (WebThing {})".format(instanceUri,actionUri,thingUri))
		sparql =  jsap_obj.getQuery("GET_ACTION_COMPLETION_AND_OUTPUT",{"thing" : thingUri,"action" : actionUri,"instance" : instanceUri})
		if output_handler is None:
			output_handler = DefaultActionCompletionHandler(kp)
		spuid = kp.subscribe(jsap_obj.subscribeUri,sparql, "CompletionOutput_{}_Notification".format(instanceUri), output_handler)
		output_handler.setSubID(spuid)
		if input_value is None:
			logger.info("Requesting instance {} for Action {} (WebThing {}) - no input given".format(instanceUri,actionUri,thingUri))
			sparql = jsap_obj.getUpdate("POST_ACTION_INSTANCE_NO_INPUT",{"action" : actionUri,"instance" : instanceUri})
		else:
			logger.info("Requesting instance {} for Action {} (WebThing {}) - input: {}".format(instanceUri,actionUri,thingUri,input_value))
			sparql = jsap_obj.getUpdate("POST_ACTION_INSTANCE_WITH_INPUT",{"action" : actionUri,"instance" : instanceUri,"value" : input_value})
		kp.update(jsap_obj.updateUri,sparql)
		return instanceUri

	@staticmethod
	def waitActionConfirmation(jsap_obj,instanceUri,handler):
		kp = LowLevelKP.LowLevelKP()
		logger.info("Subscribing to confirmation timestamp for ActionInstance {}".format(instanceUri))
		sparql = jsap_obj.getQuery("GET_CONFIRMATION_TIMESTAMP",{"instance" : instanceUri})
		return (kp,kp.subscribe(jsap_obj.subscribeUri,sparql, "ActionConfirmation_{}_Notification".format(instanceUri), handler))

	@staticmethod
	def getActionList(jsap_obj,thingUri=None):
		kp = LowLevelKP.LowLevelKP()
		if thingUri is None:
			sparql = jsap_obj.getQuery("LIST_ACTIONS",{})
		else:
			sparql = jsap_obj.getQuery("LIST_ACTIONS",{"thing" : thingUri})
		status,results = kp.query(jsap_obj.queryUri,sparql)
		return results["results"]["bindings"]


class Event:
	"Event class object, as defined by in WoT Arces research group"
	instances = count(1)

	def __init__(self,name="Event{}".format(instances),uri=str(uuid4()),out_dataschema="",PCFlag=False):
		self.thing = None
		self._name = name
		self._uri = uri
		self.out_dataschema = out_dataschema
		self.pc_flag = PCFlag
		next(Event.instances)

	def setThing(self,thing):
		self.thing = thing.uri

	def isPropertyChangedEvent(self):
		return self.pc_flag

	def getForcedBindings(self):
		if self.thing is None:
			raise ValueError("Undefined container WebThing for {}".format(self._name))
		forcedBindings = {
			"thing" : self.thing,
			"eName" : self.name,
			"event" : self.uri,
			"outDataSchema" : self.out_dataschema }
		return forcedBindings

	@property
	def name(self):
		return self._name

	@property
	def uri(self):
		return self._uri

	@staticmethod
	def subscribeToEvent(jsap_obj,thingUri,eventUri,handler):
		kp = LowLevelKP.LowLevelKP()
		logger.info("Subscribing to event {} (WebThing {})".format(eventUri,thingUri))
		sparql = jsap_obj.getQuery("GET_EVENT_NOTIFICATION",{"thing" : thingUri,"event" : eventUri})
		kp.subscribe(jsap_obj.subscribeUri,sparql, "Event_{}_Notification".format(eventUri), handler)

	@staticmethod
	def getEventList(jsap_obj,thingUri=None):
		kp = LowLevelKP.LowLevelKP()
		if thingUri is None:
			sparql = jsap_obj.getQuery("LIST_EVENTS",{})
		else:
			sparql = jsap_obj.getQuery("LIST_EVENTS",{"thing" : thingUri})
		status,results = kp.query(jsap_obj.queryUri,sparql)
		return results["results"]["bindings"]

class Property:
	"Property class object, as defined by in WoT Arces research group"
	instances = count(1)

	def __init__(self,name="Property{}".format(instances),uri=str(uuid4()),dataschema="",writable=True,stability=0,value=""):
		self.thing = None
		self._name = name
		self._uri = uri
		self.dataschema = dataschema
		self.writable = writable
		self.stability = stability
		self.value = value
		next(Property.instances)

	def getForcedBindings(self):
		if self.thing is None:
			raise ValueError("Undefined container WebThing for {}".format(self._name))
		return {
			"thing" : self.thing,
			"newName" : self._name,
			"property" : self._uri,
			"newDataSchema" : self.dataschema,
			"newWritable" : self.writable,
			"newStability" : self.stability,
			"newValue" : self.value }

	def setThing(self,thing):
		self.thing = thing.uri

	@property
	def name(self):
		return self._name

	@property
	def uri(self):
		return self._uri

	@staticmethod
	def subscribeToValueChange(jsap_obj,propertyUri,handler,secure=False):
		kp = LowLevelKP.LowLevelKP()
		logger.info("Subscribing to property {} value change".format(propertyUri))
		sparql = jsap_obj.getQuery("GET_EVENT_NOTIFICATION",{"thing" : thingUri,"event" : eventUri})
		return (kp,kp.subscribe(jsap_obj.subscribeUri,sparql, "Property_{}_value_subscription".format(propertyUri), handler))

	@staticmethod
	def getPropertyList(jsap_obj,thingUri=None):
		kp = LowLevelKP.LowLevelKP()
		if thingUri is None:
			sparql = jsap_obj.getQuery("LIST_PROPERTIES",{})
		else:
			sparql = jsap_obj.getQuery("LIST_PROPERTIES",{"thing" : thingUri})
		status,results = kp.query(jsap_obj.queryUri,sparql)
		return results["results"]["bindings"]
