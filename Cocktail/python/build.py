import sys

sys.path.insert(0, "src/main/python")
from pybuilder.core import use_plugin, init

use_plugin("python.core")
use_plugin("python.unittest")
use_plugin("python.install_dependencies")
#use_plugin("python.coverage")
use_plugin("python.distutils")


name = "Cocktail"
default_task = "publish"


@init
def set_properties(project):
    project.depends_on('PyLD')
    project.depends_on('pyfakefs')
    pass
