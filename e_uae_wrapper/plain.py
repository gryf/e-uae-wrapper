#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Plain class for executing e-uae with specified parameters. This is useful for
running things from floppies. It creates new .uaerc file with substituted all
templates with proper values and run. Floppies usually are unpacked or only
gzipped (which is supported by emulator itself) so there is no need to copy
them to temporary place.
Unlike other modules, there is no path changing during running e-uae.
"""
import os

from e_uae_wrapper import base
from e_uae_wrapper import utils


class Wrapper(base.Base):
    """Plain class for running e-uae"""

    def run(self):
        """
        Main function which run e-uae
        """
        if not super(Wrapper, self).run():
            return False

        self._run_emulator()

    def _validate_options(self):
        """No options needed for this module"""
        return True

    def _run_emulator(self):
        """execute e-uae"""
        utils.run_command(['e-uae', '-f', os.path.join(self.dir, '.uaerc')])
