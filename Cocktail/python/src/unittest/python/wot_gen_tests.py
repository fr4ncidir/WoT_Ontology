from unittest import TestCase
from pybuilder.core import Project, Logger,Dependency
from pybuilder.utils import read_file
from pybuilder_cocktail import *
from pyfakefs.fake_filesystem_unittest import Patcher
import os.path
from webthing import *
from jsap import *
import thing_parser
import sys

class WotGenTests(TestCase):
    def setUp(self):
        with Patcher() as patcher:
            patcher.fs.CreateDirectory('testproject')
            patcher.fs.CreateDirectory('src/main/python')
            self.project = Project('testproject')
            self.project.set_property('dir_source_main_python','src/main/python')
        self.logger = Logger()

    def test_add_dep(self):
         cocktail_dependencies(self.project)
         self.assertTrue( Dependency("sepy",url="git+https://github.com/arces-wot/SEPA-python3-APIs") in self.project.dependencies)
         self.assertTrue( Dependency("colorama") in self.project.dependencies)

    def test_retrieve_src_for_things(self):
        res = retrieve_src_for_things(self.project)
        if sys.platform in ['win32']:
            self.assertEquals(res,'src\\main\\things')
        else:
            self.assertEquals(res,'src/main/things')
        self.assertTrue(os.path.exists(res))

        self.project.things_path = 'things'
        res = retrieve_src_for_things(self.project)
        self.assertEquals(res,'things')

    def test_list_thing_descriptors(self):
        with Patcher() as patcher:
            patcher.fs.CreateFile('/things/thing1.jsonld')
            patcher.fs.CreateFile('/things/thing2.jsonld')
            patcher.fs.CreateFile('/things/thing2.json')
            patcher.fs.CreateFile('/things/thing4.txt')
            res = list_thing_descriptors('/things')
            r = []
            for item in res:
                r.append(item)

        if sys.platform in ['win32']:
            self.assertTrue('\\things\\thing1.jsonld' in r)
            self.assertTrue('\\things\\thing2.jsonld' in r)
            self.assertFalse('\\things\\thing2.json' in r)
            self.assertFalse('\\things\\thing4.txt' in r)
        else:
            self.assertTrue('/things/thing1.jsonld' in r)
            self.assertTrue('/things/thing2.jsonld' in r)
            self.assertFalse('/things/thing2.json' in r)
            self.assertFalse('/things/thing4.txt' in r)

    def test_remove_already_existing(self):
        with Patcher() as patcher:
            patcher.fs.CreateFile('/fakesrc/thing1.py')
            patcher.fs.CreateFile('/fakesrc/thing2.py')
            patcher.fs.CreateFile('/fakesrc/thing.py')
            patcher.fs.CreateFile('/fakesrc/pippo.py')

            patcher.fs.CreateFile('/fakesrc/fake.jsap',contents=fake_td)

            thing1 = WebThing('/fakesrc/fake.jsap','thing1')
            thing2 = WebThing('/fakesrc/fake.jsap','thing2')
            lamp = WebThing('/fakesrc/fake.jsap','lamp')
            sensor = WebThing('/fakesrc/fake.jsap','sensor')

            wts = []
            wts.append(thing1)
            wts.append(thing2)
            wts.append(lamp)
            wts.append(sensor)

            res = find_already_existing('/fakesrc',wts)

            print(res)
            self.assertIn(thing1,res)
            self.assertIn(thing2,res)
            self.assertNotIn(lamp,res)
            self.assertNotIn(sensor,res)
    def test_jsonLD_parser(self):
        if sys.platform in ["win32"]:        
            res = "src\\main\\things\\thing_example.jsonld"
        else:
            res = "src/main/things/thing_example.jsonld"
        self.assertTrue(os.path.exists(res))
            
        wt = thing_parser.jsonLD2Thing("".join(read_file(res)))
        self.assertTrue(wt.name=="MyLamp")
        self.assertTrue(len(wt.properties)==1)
        self.assertTrue(len(wt.actions)==2)
