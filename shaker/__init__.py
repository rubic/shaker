"""
Build and lauch EBS instances as salt minions.
"""
from shaker.version import __version__

import os
import optparse
import shaker.log
import shaker.config
LOG = shaker.log.getLogger(__name__)


class EBSFactory(object):
    """EBSFactory - build and launch EBS salt minions.
    """
    def __init__(self):
        self.cli = self.parse_cli()


    def process(self):
        pass

    def parse_cli(self):
        parser = optparse.OptionParser(
            usage="%prog [options] profile",
            version="%%prog %s" % __version__,
        )
        parser.add_option('-a', '--ami', dest='ec2_ami_id', metavar='AMI',
                          help='build instance from AMI')
        parser.add_option('-g', '--group', dest='ec2_security_group', default=None)
        parser.add_option('--config-dir', dest='config_dir', help="configuration directory")
        parser.add_option('', '--nouser', dest='nouser',
                          action='store_true', default=False,
                          help='create no user')
        parser.add_option('-t', '--test', dest='test_mode',
                          action='store_true', default=False,
                          help='test mode')
        (opts, args) = parser.parse_args()
        if len(args) < 1:
            print parser.format_help().strip()
            raise SystemExit("Specify shaker profile")

        import shaker.config
        opts.config_dir = shaker.config.init_directory(opts)

        import shaker.log
        shaker.log.start_logger(__name__,
                                os.path.join(opts.config_dir, 'shaker.log'))
        LOG.info("Just some logged info.")
