import logging

log = logging.getLogger(__name__)
config = None


def configure(new_config):
    global config
    config = new_config
    """Configure this module, given the config."""
    log.info("Initializing RIPE Atlas Plugin with api key {}".format(config.get('api_key')))


def get_config():
    global config
    return config
