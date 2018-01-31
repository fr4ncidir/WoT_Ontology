from unittest import TestCase
from pybuilder.core import Project, Logger,Dependency
from pybuilder_cocktail import cocktail_dependices

class WotGenTests(TestCase):
    def setUp(self):
        self.project = Project("basedir")
        self.logger = Logger()

    def test_add_dep(self):
         cocktail_dependices(self.project)
         self.assertTrue( Dependency("sepy",None,None) in self.project.dependencies)
