from pybuilder.core import task,depends,before

@task("cocktail_dependices", description="Add cocktail dependencies to your Project")
@before("install_dependencies", only_once=True)
def cocktail_dependices(project):
    project.depends_on('sepy')

@task("generate_things", description="Reads your TDs and creates Py things")
@depends('cocktail_dependices')
def generate_things(project, logger):
    #Load data from JSON-LD TDs in project class path
