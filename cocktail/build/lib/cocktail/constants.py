#!/usr/bin python3
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

from pkg_resources import resource_filename

# Plain SPARQL
SPARQL_QUERY_ALL = "select * where {?a ?b ?c}"
SPARQL_DELETE_ALL = "delete where {?a ?b ?c}"

# Setup inserts
SPARQL_INSERT_THING1 = resource_filename(__name__, "setups/insert_thing_1.sparql")
SPARQL_INSERT_THING2 = resource_filename(__name__, "setups/insert_thing_2.sparql")
SPARQL_INSERT_THING3 = resource_filename(__name__, "setups/insert_thing_3.sparql")

# Queries
PATH_SPARQL_QUERY_THING = resource_filename(__name__, "queries/thing.sparql")
PATH_SPARQL_QUERY_PROPERTY = resource_filename(__name__, "queries/property.sparql")
PATH_SPARQL_QUERY_ACTION = resource_filename(__name__, "queries/action.sparql")
PATH_SPARQL_QUERY_EVENT = resource_filename(__name__, "queries/event.sparql")
PATH_SPARQL_QUERY_ACTION_INSTANCE = resource_filename(__name__, "subscribes/action_instance.sparql")
PATH_SPARQL_QUERY_EVENT_INSTANCE = resource_filename(__name__, "subscribes/event_instance.sparql")
PATH_SPARQL_QUERY_TS_TEMPLATE = resource_filename(__name__, "subscribes/{}_ts.sparql")
PATH_SPARQL_QUERY_INSTANCE_OUTPUT = resource_filename(__name__, "subscribes/instance_output.sparql")
PATH_SPARQL_QUERY_DATASCHEMA = resource_filename(__name__, "queries/data_schema.sparql")
PATH_SPARQL_QUERY_INTERACTION_PATTERN = resource_filename(__name__, "queries/interaction_pattern.sparql")

# Updates
PATH_SPARQL_NEW_THING = resource_filename(__name__, "updates/new_thing.sparql")
PATH_SPARQL_NEW_SUBTHING = resource_filename(__name__, "updates/new_subthing.sparql")
PATH_SPARQL_NEW_DATASCHEMA = resource_filename(__name__, "updates/new_dataschema.sparql")
PATH_SPARQL_NEW_PROPERTY = resource_filename(__name__, "updates/new_property.sparql")
PATH_SPARQL_ADD_FORPROPERTY = resource_filename(__name__, "updates/add_forProperty.sparql")
PATH_SPARQL_NEW_ACTION_TEMPLATE = resource_filename(__name__, "updates/new_{}_action.sparql")
PATH_SPARQL_NEW_EVENT_TEMPLATE = resource_filename(__name__, "updates/new_{}_event.sparql")
PATH_SPARQL_NEW_ACTION_INSTANCE_TEMPLATE = resource_filename(__name__, "updates/new_{}_action_instance.sparql")
PATH_SPARQL_NEW_EVENT_INSTANCE_TEMPLATE = resource_filename(__name__, "updates/new_{}_event_instance.sparql")
PATH_SPARQL_NEW_TS_TEMPLATE = resource_filename(__name__, "updates/new_{}_ts.sparql")
PATH_SPARQL_NEW_INSTANCE_OUTPUT = resource_filename(__name__, "updates/new_action_instance_output.sparql")

# Deletes
PATH_SPARQL_DELETE_THING = resource_filename(__name__, "deletes/del_thing.sparql")
PATH_SPARQL_DELETE_IP = resource_filename(__name__, "deletes/del_interaction_pattern.sparql")
PATH_SPARQL_DELETE_ACTION_INSTANCE = resource_filename(__name__, "deletes/del_action_instance.sparql")
PATH_SPARQL_DELETE_EVENT_INSTANCE = resource_filename(__name__, "deletes/del_event_instance.sparql")

# Results to queries
RES_SPARQL_QUERY_ALL = resource_filename(__name__, "queries/results/res_query_all.json")
RES_SPARQL_QUERY_ALL_NEW_DATASCHEMA = resource_filename(__name__, "updates/results/res_query_all_new_dataschema.json")
RES_SPARQL_QUERY_ALL_NEW_DS_ACTIONS = resource_filename(__name__, "updates/results/res_query_all_new_dataschema_actions.json")
RES_SPARQL_QUERY_ALL_NEW_DS_EVENTS = resource_filename(__name__, "updates/results/res_query_all_new_dataschema_events.json")

# Results to updates
RES_SPARQL_NEW_PROPERTY = resource_filename(__name__, "updates/results/res_new_property_create.json")
RES_SPARQL_NEW_PROPERTY_UPDATE = resource_filename(__name__, "updates/results/res_new_property_update.json")
RES_SPARQL_NEW_THING = resource_filename(__name__, "updates/results/res_new_thing.json")
RES_SPARQL_NEW_ACTIONS = resource_filename(__name__, "updates/results/res_new_actions_create.json")
RES_SPARQL_NEW_EVENTS = resource_filename(__name__, "updates/results/res_new_events_create.json")

# Subscriptions expected results
RES_SPARQL_NEW_ACTION_INSTANCE_TEMPLATE = resource_filename(__name__, "subscribes/results/res_new_{}_action_instance.json")
RES_SPARQL_NEW_ACTION_INSTANCE_UPDATE_TEMPLATE = resource_filename(__name__, "subscribes/results/res_new_{}_action_instance_update.json")
RES_SPARQL_NEW_ACTION_INSTANCE_UPDATE = resource_filename(__name__, "subscribes/results/res_new_action_instance_update.json")
RES_SPARQL_NEW_EVENT_INSTANCE_TEMPLATE = resource_filename(__name__, "subscribes/results/res_new_{}_event_instance.json")
RES_SPARQL_NEW_EVENT_INSTANCE_UPDATE_TEMPLATE = resource_filename(__name__, "subscribes/results/res_new_{}_event_instance_update.json")
RES_SPARQL_NEW_TS_TEMPLATE = resource_filename(__name__, "subscribes/results/res_new_{}_ts.json")
RES_SPARQL_NEW_INSTANCE_OUTPUT = resource_filename(__name__, "subscribes/results/res_new_instance_output.json")

SPARQL_PREFIXES = """prefix xsd: <http://www.w3.org/2001/XMLSchema#>
prefix owl: <http://www.w3.org/2002/07/owl#>
prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
prefix dul: <http://www.ontologydesignpatterns.org/ont/dul/DUL.owl#>
prefix wot: <http://wot.arces.unibo.it/ontology/web_of_things#>"""