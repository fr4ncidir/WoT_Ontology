Ontotest.py explanation
====================

Within this file, we explain how the ontotest.py script performs query, update and delete tests using the Web Of Things ontology as SPARQL pattern.

## 1. Setting up the test data
The first step is of course to define a base for the test. That is, we clear up the RDF store with
```
DELETE WHERE {?a ?b ?c}
```
Then, we proceed to insertion of two WebThings. The first is built as the following:
|                           Thing |   uri   | &lt;http://MyFirstWebThing.com&gt;                               |
|--------------------------------:|:-------:|------------------------------------------------------------------|
|                      Thing Name | literal | 'Thing1'                                                         |
|               Thing-Description |   uri   | &lt;http://MyFirstWebThingDescription.com&gt;                    |
|               Number of Actions |         | 2                                                                |
|                Number of Events |         | 1                                                                |
|            Number of Properties |         | 1                                                                |
|                        Action 1 |   uri   | &lt;http://MyFirstWebThing.com/Action1&gt;                       |
|                   Action 1 Name | literal | 'Thing1_Action1'                                                 |
|        Action 1 InputDataSchema |   uri   | &lt;http://MyFirstWebThing.com/Action1/DataSchema/input&gt;      |
|       Action 1 OutputDataSchema |   uri   | &lt;http://MyFirstWebThing.com/Action1/DataSchema/output&gt;     |
|    Action 1 InputDS FieldSchema |   uri   | xsd:string                                                       |
|   Action 1 OutputDS FieldSchema |   uri   | &lt;www.wikipedia.it&gt;                                         |
|                        Action 2 |   uri   | <http://MyFirstWebThing.com/Action2>                             |
|                   Action 2 Name | literal | 'Thing1_Action2'                                                 |
|       Action 2 OutputDataSchema |   uri   | <http://MyFirstWebThing.com/Action2/DataSchema/output>           |
|   Action 2 OutputDS FieldSchema |   uri   | xsd:integer                                                      |
|                           Event |   uri   | <http://MyFirstWebThing.com/Event1>                              |
|                      Event Name | literal | 'Thing1_Event1'                                                  |
|          Event OutputDataSchema |   uri   | &lt;http://MyFirstWebThing.com/Event1/DataSchema/output&gt;      |
|      Event OutputDS FieldSchema |   uri   | xsd:dateTimeStamp                                                |
|                        Property |   uri   | &lt;http://MyFirstWebThing.com/Property1&gt;                     |
|                   Property Name | literal | 'Thing1_Property1'                                               |
|              Property Stability | literal | '1000'                                                           |
|            Property Writability | literal | 'true'                                                           |
|            Property forProperty |   uri   | &lt;http://MyFirstWebThing.com/Action2&gt;                       |
|     Property PropertyDataSchema |   uri   | &lt;http://MyFirstWebThing.com/Property1/DataSchema/property&gt; |
| Property PropertyDS FieldSchema |   uri   | xsd:string                                                       |
|           Property PropertyData |   uri   | <http://MyFirstWebThing.com/Property1/PropertyData>              |
|          Property initial value | literal | 'Hello World!'                                                   |

and the second instead is
|                           Thing |   uri   | &lt;http://MySecondWebThing.com&gt;                              |
|--------------------------------:|:-------:|------------------------------------------------------------------|
|                      Thing Name | literal | 'Thing2'                                                         |
|               Thing-Description |   uri   | &lt;http://MySecondWebThingDescription.com&gt;                   |
|               Number of Actions |         | 1                                                                |
|                Number of Events |         | 2                                                                |
|            Number of Properties |         | 2                                                                |
|                        Action 1 |   uri   | &lt;http://MySecondWebThing.com/Action1&gt;                      |
|                     Action Name | literal | 'Thing2_Action1'                                                 |
|          Action InputDataSchema |   uri   | &lt;http://MySecondWebThing.com/Action1/DataSchema/input&gt;     |
|         Action OutputDataSchema |   uri   | &lt;http://MySecondWebThing.com/Action1/DataSchema/output&gt;    |
|      Action InputDS FieldSchema |   uri   | foaf                                                             |
|     Action OutputDS FieldSchema |   uri   | xsd:string                                                       |
|                         Event 1 |   uri   | &lt;http://MySecondWebThing.com/Event1&gt;                       |
|                    Event 1 Name | literal | 'Thing2_Event1'                                                  |
|        Event 1 OutputDataSchema |   uri   | &lt;http://MySecondWebThing.com/Event1/DataSchema/output&gt;     |
|    Event 1 OutputDS FieldSchema |   uri   | xsd:integer                                                      |
|                         Event 2 |   uri   | &lt;http://MySecondWebThing.com/Event2&gt;                       |
|                    Event 2 Name | literal | 'Thing2_Event2'                                                  |
|        Event 2 OutputDataSchema |   uri   | &lt;http://MySecondWebThing.com/Event2/DataSchema/output&gt;     |
|    Event 2 OutputDS FieldSchema |   uri   | &lt;www.wikipedia.it&gt;                                         |
|                        Property 1 |   uri   | &lt;http://MySecondWebThing.com/Property1&gt;                     |
|                   Property 1 Name | literal | 'Thing2_Property1'                                                |
|              Property 1 Stability | literal | '0'                                                               |
|            Property 1 Writability | literal | 'false'                                                           |
|            Property 1 forProperty |   uri   | &lt;http://MySecondWebThing.com/Action1&gt;                       |
|     Property 1 PropertyDataSchema |   uri   | &lt;http://MySecondWebThing.com/Property1/DataSchema/property&gt; |
| Property 1 PropertyDS FieldSchema |   uri   | xsd:Literal                                                       |
|           Property 1 PropertyData |   uri   | &lt;http://MySecondWebThing.com/Property1/PropertyData&gt;        |
|          Property 1 initial value | literal | '{"json":"content"}'                                              |
|                        Property 2 |   uri   | &lt;http://MySecondWebThing.com/Property2&gt;                     |
|                   Property 2 Name | literal | 'Thing2_Property2'                                                |
|              Property 2 Stability | literal | '75'                                                              |
|            Property 2 Writability | literal | 'true'                                                            |
|            Property 2 forProperty |   uri   | &lt;http://MySecondWebThing.com/Action1&gt; ,  &lt;http://MySecondWebThing.com/Event1&gt;   |
|     Property 2 PropertyDataSchema |   uri   | &lt;http://MySecondWebThing.com/Property2/DataSchema/property&gt; |
| Property 2 PropertyDS FieldSchema |   uri   | xsd:Literal                                                       |
|           Property 2 PropertyData |   uri   | &lt;http://MySecondWebThing.com/Property2/PropertyData&gt;        |
|          Property 2 initial value | literal | 'Whatever kind of binary content'                                 |
The SPARQL inserts of those two tables can be found in *insert_thing_1.sparql* and in *insert_thing_2.sparql* files.
