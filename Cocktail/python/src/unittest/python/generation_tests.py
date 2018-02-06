from unittest import TestCase
from pybuilder_cocktail import *
from pyfakefs.fake_filesystem_unittest import Patcher
import os.path
from webthing import *
from jsap import *
import ast

class WotGenTests(TestCase):

    def test_empty_generation(self):
        with Patcher() as patcher:
            patcher.fs.CreateFile('/fakesrc/fake.jsap',contents=fake_td)
            heater = WebThing('/fakesrc/fake.jsap','empty')

            generate('/fakesrc',heater)
            self.assertTrue(os.path.exists('/fakesrc/empty.py'))
            with open("/fakesrc/empty.py") as f:
                content = f.readlines()
                content = "".join(content)
                try:
                    #assure that the file has no syntax errors
                    ast.parse(content,"heater.py","exec")
                except:
                    print('Malformed file:')
                    print(content)
                    raise

    def test_generation(self):
        with Patcher() as patcher:
            patcher.fs.CreateFile('/fakesrc/fake.jsap',contents=fake_td)

            heater = WebThing('/fakesrc/fake.jsap','heater')
            power = Property(heater,"Power",uri="wot:Power",dataschema="float",writable=False,value="0")
            on =    Action(  heater,name="On",uri="wot:HeaterOn")
            off =   Action(  heater,name="Off",uri="wot:HeaterOff")

            heater.add_property(power)
            heater.add_action(on)
            heater.add_action(off)
            heater.add_forProperty(on,power)
            heater.add_forProperty(off,power)

            generate('/fakesrc',heater)

            self.assertTrue(os.path.exists('/fakesrc/heater.py'))
            with open("/fakesrc/heater.py") as f:
                content = f.readlines()
                content = "".join(content)
                try:
                    #assure that the file has no syntax errors
                    ast.parse(content,"heater.py","exec")
                except:
                    print('Malformed file:')
                    print(content)
                    raise
