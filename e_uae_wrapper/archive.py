"""
Run e-uae with archived filesystem/adf files

It will use compressed directories, and optionally replace source archive with
the temporary one.
"""
import os
import shutil

from e_uae_wrapper import base
from e_uae_wrapper import utils


class Wrapper(base.ArchiveBase):
    """
    Class for performing extracting archive, copying emulator files, and
    cleaning it back again
    """
    def __init__(self, conf_path, configuration):
        super(Wrapper, self).__init__(conf_path, configuration)
        self.archive_type = None

    def run(self):
        """
        Main function which accepts configuration file for e-uae
        It will do as follows:
            - extract archive file
            - copy configuration
            - run the emulation
            - optionally make archive save state
        """
        if not super(Wrapper, self).run():
            return False

        if not self._extract():
            return False

        if not self._copy_conf():
            return False

        if not self._run_emulator():
            return False

        return self._make_archive()

    def _make_archive(self):
        """
        Produce archive and save it back. Than remove old one.
        """
        if self.config.get('wrapper_persist_data', '0') != '1':
            return True

        curdir = os.path.abspath('.')
        os.chdir(self.dir)

        os.unlink('.uaerc')

        title = self._get_title()

        arch = os.path.basename(self.arch_filepath)
        if not utils.create_archive(arch, title):
            return False

        shutil.move(arch, self.arch_filepath)
        os.chdir(curdir)
        return True
