"""
Misc utilities
"""
import collections
import logging
import os
import subprocess
try:
    import configparser
except ImportError:
    import ConfigParser as configparser

from e_uae_wrapper import file_archive


def load_conf(conf_file):
    """
    Read global config and provided config file and return dict with combined
    options."""
    conf = _get_common_config()
    local_conf = collections.OrderedDict()

    with open(conf_file) as fobj:
        for line in fobj:
            key, val = line.strip().split('=')
            if key in local_conf:
                raise Exception('%s already in conf' % key)
            local_conf[key] = val

    conf.update(local_conf)
    return conf


def operate_archive(arch_name, operation, text, params):
    """
    Create archive from contents of current directory
    """

    archiver = file_archive.get_archiver(arch_name)

    if archiver is None:
        return False

    res = False

    if operation == 'extract':
        res = archiver.extract(arch_name)

    if operation == 'create':
        res = archiver.create(arch_name, params)

    return res


def create_archive(arch_name, title='', params=None):
    """
    Create archive from contents of current directory
    """
    msg = ''
    if title:
        msg = "Creating archive for `%s'. Please be patient" % title
    return operate_archive(arch_name, 'create', msg, params)


def extract_archive(arch_name, title='', params=None):
    """
    Extract provided archive to current directory
    """
    msg = ''
    if title:
        msg = "Extracting files for `%s'. Please be patient" % title
    return operate_archive(arch_name, 'extract', msg, params)


def run_command(cmd):
    """
    Run provided command. Return true if command execution returns zero exit
    code, false otherwise. If cmd is not a list, there would be an attempt to
    split it up for subprocess call method. May throw exception if cmd is not
    a list neither a string.
    """

    if not isinstance(cmd, list):
        cmd = cmd.split()

    logging.debug("Executing `%s'.", " ".join(cmd))
    code = subprocess.call(cmd)
    if code != 0:
        logging.error('Command `%s` returned non 0 exit code.', cmd[0])
        return False
    return True


def _get_common_config():
    """
    Try to find common configuration file and return data as a dict.
    File will be gather from $XDG_CONFIG_HOME/e-uaerc, which ususally is
    ~/.config/e-uaerc
    """

    parser = configparser.SafeConfigParser()

    xdg_conf = os.getenv('XDG_CONFIG_HOME', os.path.expanduser('~/.config'))
    conf_path = os.path.join(xdg_conf, 'e-uae.ini')

    try:
        parser.read(conf_path)
    except configparser.ParsingError:
        logging.warning("Configuration is in wrong ini format and cannot be"
                        " parsed.")
        return {}

    try:
        section = parser.sections()[0]
    except IndexError:
        logging.warning("Configuration lacks of required section.")
        return {}

    conf = collections.OrderedDict()
    for option in parser.options(section):
        if option in ['wrapper_rom_path']:
            conf[option] = parser.get(section, option)

    return conf


def get_arch_ext(archiver_name):
    """Return extension for the archiver"""
    return file_archive.Archivers.get_extension_by_name(archiver_name)
