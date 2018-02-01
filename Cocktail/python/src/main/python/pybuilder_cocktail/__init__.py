from pybuilder.core import task,depends,before
from pybuilder.utils import mkdir,discover_files
from pathlib import Path
from pybuilder.errors import PyBuilderException

@task("cocktail_dependencies", description="Add cocktail dependencies to your Project")
@before("install_dependencies", only_once=True)
def cocktail_dependencies(project):
    project.depends_on('sepy')

@task("generate_things", description="Reads your TDs and creates Py things")
@depends('cocktail_dependencies')
def generate_things(project, logger):
    logger.info("Thanks for your order...")
    logger.info("Finding ingredients...")

    thing_dir = retrieve_src_for_things(project)
    logger.debug("thing path set to: %s" % thing_dir)

    if not Path(thing_dir).exists():
        raise PyBuilderException("Thing path not vaild %s" % thing_dir )

    #Load data from JSON-LD TDs in project class path

    tds = list_thing_descriptors(thing_dir)
    wts = read_web_things(tds)
    logger.debug("Correctly found %d web things" % len(wts))

    logger.info("Mixing...")
    src = project.get_property('dir_source_main_python')
    already_existing_things = remove_already_existing(src,wts)
    generate(src,wts)

    logger.info("Shaking...")
    update(already_existing_things)

    logger.info("There you are!")

def remove_already_existing(src,wts):

def generate(src,wts):


def read_web_things(tds):
    wts = []
    for td in tds:
        try:
            wt = jsonLD2Thing(td)
            wts.append(wt)
        except Exception as e:
            raise
    return wts

def retrieve_src_for_things(project):
    try:
        things_dir = project.things_path
    except AttributeError:
        src = project.get_property('dir_source_main_python')
        parent = Path(src).parent
        things_dir = str(parent / 'things')
        mkdir(things_dir)
    return things_dir

def list_thing_descriptors(dir):
    return discover_files(dir,'.jsonld')
