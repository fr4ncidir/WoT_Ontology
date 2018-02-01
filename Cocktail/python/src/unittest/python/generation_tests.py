from unittest import TestCase
from pybuilder_cocktail import *
from pyfakefs.fake_filesystem_unittest import Patcher
import os.path
from webthing import *
from jsap import *
import importlib.util

class WotGenTests(TestCase):

    def test_generation(self):
        with Patcher() as patcher:
            patcher.fs.CreateFile('/fakesrc/fake.jsap',contents=fake_td)
            heater = WebThing('/fakesrc/fake.jsap','heater')

            generate('/fakesrc',heater)

            self.assertTrue(os.path.exists('/fakesrc/heater.py'))
