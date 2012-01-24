"""
Build and lauch EBS instances as salt minions.
"""
from shaker.version import __version__

import optparse

class EBSFactory(object):
    """EBSFactory - build and launch EBS salt minions.
    """
    def __init__(self):
        self.cli = self.parse_cli()

    def process(self):
        pass

    def parse_cli(self):
        pass
