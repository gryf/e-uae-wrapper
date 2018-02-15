#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Simple class for executing e-uae with specified parameters. This is a
failsafe class for running e-uae.
"""
from e_uae_wrapper import base
from e_uae_wrapper import utils


class Wrapper(base.Base):
    """Simple class for running e-uae"""

    def run(self):
        """
        Main function which run e-uae
        """
        self._run_emulator()

    def _run_emulator(self):
        """execute e-uae"""
        utils.run_command(['e-uae', self.conf_file])

    def clean(self):
        """Do the cleanup. Here - just do nothing"""
        return
