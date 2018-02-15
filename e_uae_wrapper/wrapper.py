#!/usr/bin/env python
"""
Wrapper for e-uae to perform some actions before and or after running the
emulator, if appropriate option is enabled.
"""
import argparse
import importlib
import logging
import os
import sys

from e_uae_wrapper import utils
from e_uae_wrapper import WRAPPER_KEY


def setup_logger(args):
    """Setup logger format and level"""

    level = logging.WARNING

    if args.quiet:
        level = logging.ERROR
        if args.quiet > 1:
            level = logging.CRITICAL

    if args.verbose:
        level = logging.INFO
        if args.verbose > 1:
            level = logging.DEBUG

    logging.basicConfig(level=level,
                        format="%(asctime)s %(levelname)s: %(message)s")


def parse_args():
    """
    Look out for config file and for config options which would be blindly
    passed to e-uae.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('config', help='Configuration file for e-uae.')
    parser.add_argument('-v', '--verbose', help='Be verbose. Adding more "v" '
                        'will increase verbosity', action="count",
                        default=None)
    parser.add_argument('-q', '--quiet', help='Be quiet. Adding more "q" will'
                        ' decrease verbosity', action="count", default=None)

    args = parser.parse_args()
    setup_logger(args)
    logging.debug("args: %s", args)

    return args


def run():
    """run wrapper module"""

    args = parse_args()
    configuration = utils.load_conf(args.config)

    if not configuration:
        logging.error('Error: Configuration file have syntax issues')
        sys.exit(2)

    wrapper_module = configuration.get(WRAPPER_KEY, 'plain')

    try:
        wrapper = importlib.import_module('e_uae_wrapper.' +
                                          wrapper_module)
    except ImportError:
        logging.error("Error: provided wrapper module: `%s' doesn't "
                      "exists.", wrapper_module)
        sys.exit(3)

    runner = wrapper.Wrapper(os.path.abspath(args.config), configuration)

    try:
        exit_code = runner.run()
    finally:
        runner.clean()

    if not exit_code:
        sys.exit(4)


if __name__ == "__main__":
    run()
