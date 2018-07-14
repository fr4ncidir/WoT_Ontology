# Cocktail
Within this repository we store all the necessary to start with a Web Of Things implementation. 

### 1. WoT Ontology
The file called `wot_ontology.owl` contains the ontology we use to represent things. The Classes are
1. `Thing`
2. `InteractionPattern` (`Action`, `Event`, `Property`)
3. `DataSchema`
4. `FieldSchema`

And some others that are going to be described in a paper soon.

### 2. Cocktail python3 framework
Requiring [Sepy](https://github.com/arces-wot/SEPA-python3-APIs.git), you can use the framework to create applications.
First you have to run a SEPA instance, then just read up the documentation of the framework. 

You should not need to know SPARQL to use Cocktail. However, for very special needs, in the package there are all the basic SPARQL that the framework uses, from which you can take inspiration, and then apply `sepy` to perform your queries.

##### _Install_
```
$ python3 setup.py build
$ python3 setup.py sdist
$ sudo python3 setup.py \[install|develop\]
```

### 3. Tests
For now, tests are available only to check ontology consistency.
```
$ python3 setup.py test
```

### 4. Examples
##### _Coding_
To have an example on how to make a WebThing, have a look to the following files.
1. `new_thing_example.py`
2. `tools/observe_event.py`
3. `tools/request_action.py`
and in the tests of the cocktail package.
Notice that (1) is also useful to see what happens when you start using the `wotMonitor.py` tool.
(2) is a nice runnable script to observe a specific event notifications. 

##### _Available tools and experiments_
While `tools/observe_event.py` and `tools/request_action.py` are useful to learn how to program with Cocktail, they are also invokable from the python command line.
Please refer to their -h argument to see how to invoke them.

There is also `tools/wotMonitor.py`. A typical experiment with `wotMonitor.py` consists in
0. Run the SEPA
1. open a terminal, and run
```
$ cd tools
$ python3 ../new_thing_example.py
```
2. Open another terminal, and run 
```
$ python3 wotMonitor.py
```
3. call `discover`
4. call `events`
5. choose `http://MyFirstWebThing.com/Event1`
6. see that `tools/observe_event.py` is called from `wotMonitor.py`
7. again from `wotMonitor.py`, call `discover`
8. call `actions`
9. choose an action available
10. see that `tools/request_action.py` is called from `wotMonitor.py` and that it prompts you for some input, if the action needs it.
11. enjoy

### Contribute
Feel free to get in touch, if you have any question or suggestions
