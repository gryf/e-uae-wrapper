"""
Base class for all wrapper modules
"""
import logging
import os
import re
import shutil
import sys
import tempfile

from e_uae_wrapper import utils
from e_uae_wrapper import path
from e_uae_wrapper import WRAPPER_KEY


class Base(object):
    """
    Base class for wrapper modules
    """

    CONF_RE = re.compile(r'[^{]*{{(?P<replace>[^}]+)}}')

    def __init__(self, conf_file, config):
        """
        Params:
            config:  parsed lines combined from global and local config
        """
        self.config = config
        self.dir = None
        self.save_filename = None
        self.conf_file = conf_file
        self.conf_path = os.path.dirname(os.path.abspath(conf_file))

    def run(self):
        """
        Main function which accepts config file for e-uae
        It will do as follows:
            - set needed paths for templates
            - validate options
            - [extract archive file]
            - copy configuration
            - run the emulation
        """

        self.config['wrapper_tmp_path'] = self.dir = tempfile.mkdtemp()
        self.config['wrapper_config_path'] = self.conf_path
        self._interpolate_options()

        if not self._validate_options():
            return False

        if not self._copy_conf():
            return False

        return True

    def clean(self):
        """Remove temporary file"""
        if self.dir:
            shutil.rmtree(self.dir)
        return

    def _copy_conf(self):
        """copy provided configuration as .uaerc"""
        curdir = os.path.abspath('.')
        os.chdir(self.dir)

        with open(os.path.join(self.dir, '.uaerc'), 'w') as fobj:
            for key, val in self.config.items():
                if isinstance(val, list):
                    for subval in val:
                        fobj.write('%s=%s\n' % (key, subval))
                else:
                    fobj.write('%s=%s\n' % (key, val))

        os.chdir(curdir)
        return True

    def _run_emulator(self):
        """execute e-uae"""
        curdir = os.path.abspath('.')
        os.chdir(self.dir)
        utils.run_command(['e-uae'])
        os.chdir(curdir)
        return True

    def _get_title(self):
        """
        Return the title if found in config. As a fallback archive file
        name will be used as title.
        """
        title = ''
        gui_msg = self.config.get('wrapper_gui_msg', '0')
        if gui_msg == '1':
            title = self.config.get('title')
            if not title:
                title = self.config['wrapper_archive']
        return title

    def _calculate_path(self, value):
        """
        Make absoulte path by splitting the val with '{{replace}}' and by
        adding right value for replace from config.
        """
        if not isinstance(value, list):
            value = [value]

        result = []
        for val in value:
            if '{{' not in val:
                result.append(val)
                continue

            if 'path' not in val:
                match = Base.CONF_RE.match(val)
                replace = match.group('replace')
                result.append(val.replace("{{%s}}" % replace,
                                          self.config.get(replace, '')))
                continue

            for item in re.split('[,:]', val):
                if '{{' in item:
                    path = self._get_abspath(item)
                    result.append(val.replace(item, path))
                    break

        if len(value) == 1:
            return result[0]
        return result

    def _get_abspath(self, val):
        path_list = [x for y in val.split('{{') for x in y.split('}}')]
        for index, item in enumerate(path_list):
            if item in self.config:
                path_list[index] = self.config[item]

        return os.path.abspath(os.path.join(*path_list))

    def _interpolate_options(self):
        """
        Search and replace values for options which contains {{ and  }}
        markers for replacing them with correpsonding calculated values
        """
        updated_conf = {}
        for key, val in self.config.items():

            if key.startswith(WRAPPER_KEY):
                continue

            check_val = val
            if isinstance(val, list):
                check_val = " ".join(check_val)

            if '{{' + WRAPPER_KEY in check_val:
                match = Base.CONF_RE.match(check_val)
                if not match:
                    logging.warning("Possible error in configuration file on "
                                    "key %s.", key)
                    continue

                replace = match.group('replace')
                if 'path' in replace:
                    updated_conf[key] = self._calculate_path(val)
                else:
                    updated_conf[key] = val.replace("{{%s}}" % replace,
                                                    self.config.get(replace,
                                                                    ''))

        if updated_conf:
            self.config.update(updated_conf)

    def _validate_options(self):
        """Validate mandatory options"""
        if 'wrapper' not in self.config:
            logging.error("Configuration lacks of required `wrapper' option.")
            return False

        if self.config.get('wrapper_save_state', '0') == '0':
            return True

        if 'wrapper_archiver' not in self.config:
            logging.error("Configuration lacks of required "
                          "`wrapper_archiver' option.")
            return False

        if not path.which(self.config['wrapper_archiver']):
            logging.error("Cannot find archiver `%s'.",
                          self.config['wrapper_archiver'])
            return False

        return True


class ArchiveBase(Base):
    """
    Base class for archive based wrapper modules
    """
    def __init__(self, conf_path, config):
        """
        Params:
            conf_file:      a relative path to provided configuration file
            fsuae_options:  is an CmdOption object created out of command line
                            parameters
            config:  is config dictionary created out of config file
        """
        super(ArchiveBase, self).__init__(conf_path, config)
        self.arch_filepath = os.path.join(self.conf_path,
                                          config.get('wrapper_archive', ''))

    def _set_assets_paths(self):
        """
        Set full paths for archive file (without extension) and for save state
        archive file
        """
        super(ArchiveBase, self)._set_assets_paths()

        conf_abs_dir = os.path.dirname(self.conf_file)
        arch = self.config.get('wrapper_archive')
        if arch:
            if os.path.isabs(arch):
                self.arch_filepath = arch
            else:
                self.arch_filepath = os.path.join(conf_abs_dir, arch)

    def _extract(self):
        """Extract archive to temp dir"""

        title = self._get_title()
        curdir = os.path.abspath('.')
        os.chdir(self.dir)
        result = utils.extract_archive(self.arch_filepath, title)
        os.chdir(curdir)
        return result

    def _validate_options(self):

        validation_result = super(ArchiveBase, self)._validate_options()

        if 'wrapper_archive' not in self.config:
            sys.stderr.write("Configuration lacks of required "
                             "`wrapper_archive' option.\n")
            validation_result = False

        return validation_result
