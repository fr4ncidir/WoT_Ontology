from pybuilder.core import task,depends,description,before
from pybuilder.utils import mkdir,discover_files,read_file
from pybuilder.terminal import *
from pathlib import Path
from pybuilder.errors import PyBuilderException
from pybuilder_cocktail.generation import generate
from thing_parser import jsonLD2Thing

@task
@description("Add cocktail dependencies to your Project")
@before("install_dependencies", only_once=True)
def cocktail_dependencies(project):
    project.depends_on("sepy",url="git+https://github.com/arces-wot/SEPA-python3-APIs")
    project.depends_on('colorama')

@task
@description("Reads your TDs and creates Py things")
@depends('cocktail_dependencies')
def gen_things(project, logger):
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

    already_existing_things = find_already_existing(src,wts)
    for wt in already_existing_things:
        wts.remove(wt)

    tcount = generate_things(src,wts)
    logger.info("Succesfully generated %d things" % tcount)

    logger.info("Shaking...")
    ask_overwrite(src,already_existing_things,logger)

    logger.info("There you are!")

def find_already_existing(src,wts):
    src_files = discover_files(src,'.py')
    removed = []

    for _file in src_files:
        name = Path(_file).name
        has_same_name = lambda wt,file_name=name: ((wt.name + '.py') == file_name)
        things_found = filter(has_same_name,wts)
        removed.extend(list(things_found))

    return removed


def generate_things(src,wts):
    count = 0
    for wt in wts:
        generate(src,wt)
        count = count + 1
    return count

def ask_overwrite(src,wts,logger):
    for wt in wts:
        heading = (bold(styled_text("[ASK]", fg(CYAN))),bold(styled_text(wt.name, fg(RED))))
        res = input("%s   %s already exists, do you want to overwrite it?(y/n)" % heading)
        while(res != "y" and res != "n" ):
            res = input("please use n or y:")
        if(res == "y"):
            generate(src,wt)
            logger.info("%s generated %s.py" % (styled_text("Succesfully", fg(GREEN)),wt.name))
        pass

def read_web_things(tds):
    wts = []
    for td in tds:
        try:
            jsonld = "".join(read_file(td))
            wt = jsonLD2Thing(jsonld)
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

def list_thing_descriptors(directory):
    return discover_files(directory,'.jsonld')
