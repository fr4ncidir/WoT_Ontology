import pkg_resources

from jinja2 import Template
from pybuilder.utils import write_file

_resource_package = 'pybuilder_cocktail' # Could be any module/package name
_resource_path = '/'.join(('templates', 'thing.tpl'))

_template_data = pkg_resources.resource_string(_resource_package, _resource_path)
_template = Template(str(_template_data))

def generate(src,wt):
    path = "%s/%s.py" % (src,wt.name)
    write_file(path,_template.render(thing=wt))
