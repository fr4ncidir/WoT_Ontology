#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  constants.py
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

# Plain SPARQL
SPARQL_QUERY_ALL = "select * where {?a ?b ?c}"
SPARQL_DELETE_ALL = "delete where {?a ?b ?c}"

# Setup inserts
SPARQL_INSERT_THING1 = "./setups/insert_thing_1.sparql"
SPARQL_INSERT_THING2 = "./setups/insert_thing_2.sparql"
SPARQL_INSERT_THING3 = "./setups/insert_thing_3.sparql"

# Queries
PATH_SPARQL_QUERY_THING = "./queries/thing.sparql"
PATH_SPARQL_QUERY_PROPERTY = "./queries/property.sparql"
PATH_SPARQL_QUERY_ACTION = "./queries/action.sparql"
PATH_SPARQL_QUERY_EVENT = "./queries/event.sparql"
PATH_SPARQL_QUERY_ACTION_INSTANCE = "./subscribes/action_instance.sparql"
PATH_SPARQL_QUERY_EVENT_INSTANCE = "./subscribes/event_instance.sparql"
PATH_SPARQL_QUERY_TS_TEMPLATE = "./subscribes/{}_ts.sparql"
PATH_SPARQL_QUERY_INSTANCE_OUTPUT = "./subscribes/instance_output.sparql"
PATH_SPARQL_QUERY_DATASCHEMA = "./queries/data_schema.sparql"

# Updates
PATH_SPARQL_NEW_THING = "./updates/new_thing.sparql"
PATH_SPARQL_NEW_SUBTHING = "./updates/new_subthing.sparql"
PATH_SPARQL_NEW_DATASCHEMA = "./updates/new_dataschema.sparql"
PATH_SPARQL_NEW_PROPERTY = "./updates/new_property.sparql"
PATH_SPARQL_ADD_FORPROPERTY = "./updates/add_forProperty.sparql"
PATH_SPARQL_NEW_ACTION_TEMPLATE = "./updates/new_{}_action.sparql"
PATH_SPARQL_NEW_EVENT_TEMPLATE = "./updates/new_{}_event.sparql"
PATH_SPARQL_NEW_ACTION_INSTANCE_TEMPLATE = "./updates/new_{}_action_instance.sparql"
PATH_SPARQL_NEW_EVENT_INSTANCE_TEMPLATE = "./updates/new_{}_event_instance.sparql"
PATH_SPARQL_NEW_TS_TEMPLATE = "./updates/new_{}_ts.sparql"
PATH_SPARQL_NEW_INSTANCE_OUTPUT = "./updates/new_action_instance_output.sparql"

# Deletes
PATH_SPARQL_DELETE_THING = "./deletes/del_thing.sparql"
PATH_SPARQL_DELETE_IP = "./deletes/del_interaction_pattern.sparql"
PATH_SPARQL_DELETE_ACTION_INSTANCE = "./deletes/del_action_instance.sparql"
PATH_SPARQL_DELETE_EVENT_INSTANCE = "./deletes/del_event_instance.sparql"

# Results to queries
RES_SPARQL_QUERY_ALL = "./queries/results/res_query_all.json"
RES_SPARQL_QUERY_ALL_NEW_DATASCHEMA = "./updates/results/res_query_all_new_dataschema.json"
RES_SPARQL_QUERY_ALL_NEW_DS_ACTIONS = "./updates/results/res_query_all_new_dataschema_actions.json"
RES_SPARQL_QUERY_ALL_NEW_DS_EVENTS = "./updates/results/res_query_all_new_dataschema_events.json"

# Results to updates
RES_SPARQL_NEW_PROPERTY = "./updates/results/res_new_property_create.json"
RES_SPARQL_NEW_PROPERTY_UPDATE = "./updates/results/res_new_property_update.json"
RES_SPARQL_NEW_THING = "./updates/results/res_new_thing.json"
RES_SPARQL_NEW_ACTIONS = "./updates/results/res_new_actions_create.json"
RES_SPARQL_NEW_EVENTS = "./updates/results/res_new_events_create.json"

# Subscriptions expected results
RES_SPARQL_NEW_ACTION_INSTANCE_TEMPLATE = "./subscribes/results/res_new_{}_action_instance.json"
RES_SPARQL_NEW_ACTION_INSTANCE_UPDATE_TEMPLATE = "./subscribes/results/res_new_{}_action_instance_update.json"
RES_SPARQL_NEW_ACTION_INSTANCE_UPDATE = "./subscribes/results/res_new_action_instance_update.json"
RES_SPARQL_NEW_EVENT_INSTANCE_TEMPLATE = "./subscribes/results/res_new_{}_event_instance.json"
RES_SPARQL_NEW_EVENT_INSTANCE_UPDATE_TEMPLATE = "./subscribes/results/res_new_{}_event_instance_update.json"
RES_SPARQL_NEW_TS_TEMPLATE = "./subscribes/results/res_new_{}_ts.json"
RES_SPARQL_NEW_INSTANCE_OUTPUT = "./subscribes/results/res_new_instance_output.json"

SPARQL_PREFIXES = """prefix xsd: <http://www.w3.org/2001/XMLSchema#>
prefix owl: <http://www.w3.org/2002/07/owl#>
prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
prefix dul: <http://www.ontologydesignpatterns.org/ont/dul/DUL.owl#>
prefix wot: <http://wot.arces.unibo.it/ontology/web_of_things#>
"""
