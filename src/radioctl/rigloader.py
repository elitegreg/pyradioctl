import logging
import yaml


def load_file(filename):
    with open(filename) as f:
        rig_definition = yaml.full_load(f)

    try:
        name = rig_definition['name']
        aliases = rig_definition['aliases']
    except KeyError as e:
        logging.error("Rig definition missing {}: {}", e.args[0], filename)

    return (name, aliases, rig_definition)
