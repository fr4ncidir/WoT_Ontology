import sys

sys.path.insert(0, "src/main/python")
from pybuilder.core import use_plugin, init

use_plugin("python.core")
use_plugin("python.unittest")
use_plugin("python.install_dependencies")
#use_plugin("python.coverage")
use_plugin("python.distutils")
use_plugin("pybuilder_cocktail")

name = "Cocktail"
default_task = ["install_dependencies","publish"]


@init
def set_properties(project):
    project.depends_on('pyfakefs')
    project.depends_on("sepy",url="git+https://github.com/arces-wot/SEPA-python3-APIs")
    project.plugin_depends_on("jinja2")
    pass
