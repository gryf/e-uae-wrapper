"""
Base class for all wrapper modules
"""
import logging
import os
import shutil
import sys
import tempfile

from e_uae_wrapper import utils
from e_uae_wrapper import path


class Base(object):
    """
    Base class for wrapper modules
    """
    def __init__(self, conf_file, config):
        """
        Params:
            config:  parsed lines combined from global and local config
        """
        self.config = config
        self.dir = None
        self.save_filename = None
        self.conf_file = conf_file

    def run(self):
        """
        Main function which accepts config file for e-uae
        It will do as follows:
            - set needed full path for asset files
            - extract archive file
            - copy configuration
            - [copy save if exists]
            - run the emulation
            - archive save state
        """
        if not self._validate_options():
            return False

        self.dir = tempfile.mkdtemp()
        self._interpolate_options()
        self._set_assets_paths()

        return True

    def clean(self):
        """Remove temporary file"""
        if self.dir:
            shutil.rmtree(self.dir)
        return

    def _set_assets_paths(self):
        """
        Set full paths for archive file (without extension) and for save state
        archive file
        """
        conf_abs_dir = os.path.dirname(os.path.abspath(self.conf_file))
        conf_base = os.path.basename(self.conf_file)
        conf_base = os.path.splitext(conf_base)[0]

        # set optional save_state
        arch_ext = utils.get_arch_ext(self.config.get('wrapper_archiver'))
        if arch_ext:
            self.save_filename = os.path.join(conf_abs_dir, conf_base +
                                              '_save' + arch_ext)

    def _copy_conf(self):
        """copy provided configuration as .uaerc"""
        shutil.copy(self.conf_file, self.dir)
        os.rename(os.path.join(self.dir, os.path.basename(self.conf_file)),
                  os.path.join(self.dir, '.uaerc'))
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

    def _save_save(self):
        """
        Get the saves from emulator and store it where configuration is placed
        """
        if self.config.get('wrapper_save_state', '0') != '1':
            return True

        os.chdir(self.dir)
        save_path = self._get_saves_dir()
        if not save_path:
            return True

        if os.path.exists(self.save_filename):
            os.unlink(self.save_filename)

        curdir = os.path.abspath('.')

        if not utils.create_archive(self.save_filename, '', [save_path]):
            logging.error('Error: archiving save state failed.')
            os.chdir(curdir)
            return False

        os.chdir(curdir)
        return True

    def _load_save(self):
        """
        Put the saves (if exists) to the temp directory.
        """
        if self.config.get('wrapper_save_state', '0') != '1':
            return True

        if not os.path.exists(self.save_filename):
            return True

        curdir = os.path.abspath('.')
        os.chdir(self.dir)
        utils.extract_archive(self.save_filename)
        os.chdir(curdir)
        return True

    def _get_saves_dir(self):
        """
        Return path to save state directory or None in cases:
            - there is no save state dir set relative to copied config file
            - save state dir is set globally
            - save state dir is set relative to the config file
            - save state dir doesn't exists
        Note, that returned path is relative not absolute
        """
        if not self.config.get('save_states_dir'):
            return None

        if self.config['save_states_dir'].startswith('$WRAPPER') and \
           '..' not in self.config['save_states_dir']:
            save = self.config['save_states_dir'].replace('$WRAPPER/', '')
        else:
            return None

        save_path = os.path.join(self.dir, save)
        if not os.path.exists(save_path) or not os.path.isdir(save_path):
            return None

        if save.endswith('/'):
            save = save[:-1]

        return save

    def _interpolate_options(self):
        """
        Search and replace values for options which contains {{ and  }}
        markers for replacing them with correpsonding calculated values
        """
        for key, val in self.config.items():
            print key, val

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
        self.arch_filepath = None

    def _set_assets_paths(self):
        """
        Set full paths for archive file (without extension) and for save state
        archive file
        """
        super(ArchiveBase, self)._set_assets_paths()

        conf_abs_dir = os.path.dirname(os.path.abspath(self.conf_file))
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
