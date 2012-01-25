import os

"""
Shaker configuration
"""

from jinja2 import Template

import yaml
try:
    yaml.Loader = yaml.CLoader
    yaml.Dumper = yaml.CDumper
except:
    pass

DEFAULT_CONFIG_FILENAME = 'default.cfg'

def init_directory(opts):
    """
    Initialize shaker configuration from cli, environment, defaults.
    """
    if opts.config_dir:
        config_dir = opts.config_dir
    elif os.environ.get('SHAKER_CONFIG_DIR'):
        config_dir = os.environ['SHAKER_CONFIG_DIR']
    else:
        config_dir = os.path.expanduser("~/.shaker")
    if not os.path.isdir(config_dir):
        os.makedirs(config_dir)
    return config_dir

def read_default_config(opts):
    defaults = {
        'ssh_port': '22',
        'ec2_zone': 'us-east-1b',
        'ec2_instance_type': 'm1.small',
        'ec2_distro': 'oneiric',
        'ec2_size': '0',
        'ec2_security_group': 'default',
        'ec2_root_device': '/dev/sda1',
        }

    default_config = os.path.join(opts.config_dir, DEFAULT_CONFIG_FILENAME)
    if not os.path.isfile(default_config):
        template = Template(DEFAULT_CONFIG)
        with open(default_config, 'w') as f:
            f.write(template.render(defaults))

    # Read default_config (YAML), which will then be overridden
    # by profile, opts ...

def read_profile(profile_pathname):
    pass


# If the default.cfg cannot be found, create it from the DEFAULT_CONFIG
# template.

DEFAULT_CONFIG = """####################################################################
# hostname, domain to assign the instance.
####################################################################

#hostname:
#domain:

####################################################################
# Install the user with sudo privileges.  If sudouser is listed
# in ssh_import, the public key will be installed from
# lauchpad.net.  From the command-line, sudouser will default
# to $LOGNAME, if not otherwise specified.
####################################################################

#sudouser:

####################################################################
# Import public keys from lauchpad.net.  Only applicable for
# Ubuntu cloud-init.  User names are comma-separated, no spaces.
####################################################################

#ssh_import:

####################################################################
# ssh_port: You may define a non-standard ssh port, but verify
# it's open in your ec2_security_group.
####################################################################

#ssh_port: {{ ssh_port }}

####################################################################
# timezone:
# e.g. timezone: America/Chicago
# http://en.wikipedia.org/wiki/List_of_tz_database_time_zones
####################################################################

#timezone:

####################################################################
# ec2_zone: if not specified, defaults to arbitrary us-east zone
####################################################################

#ec2_zone: {{ ec2_zone }}

####################################################################
# ec2_instance_type defaults to m1.small
# http://aws.amazon.com/ec2/instance-types/
####################################################################

#ec2_instance_type: {{ ec2_instance_type }}

####################################################################
# ec2_ami_id: AMI image to launch.  Note AMI's are
# region-specific, so you must specify the the appropriate AMI
# for the ec2_zone above.  ec2_ami_id overrides ec2_distro
# below.
####################################################################

#ec2_ami_id:

####################################################################
# ec2_distro: precise, oneiric, natty, maverick, lucid, hardy
# TODO: add support for Debian: sid, etc.
####################################################################

#ec2_distro: {{ ec2_distro }}

####################################################################
# ec2_size: size of the root file partition in GB.  If not
# specified (or zero), defaults to the instance type.
####################################################################

#ec2_size: {{ ec2_size }}

####################################################################
# ec2_key_name: Name of the key pair used to create the instance.
# If not specified and only one key-pair is available, it will be
# used.  Otherwise you must specify the key-pair.  Further info:
# http://docs.amazonwebservices.com/AWSEC2/latest/UserGuide/generating-a-keypair.html
####################################################################

#ec2_key_name:

####################################################################
# ec2_security_group: The security group to control port access
# to the instance (ssh, http, etc.)  If not specified, use
# 'default', which generally permits port 22 for ssh access.
####################################################################

#ec2_security_group: default

####################################################################
# ec2_monitoring_enabled:
# http://aws.amazon.com/cloudwatch/
####################################################################

#ec2_monitoring_enabled: false

####################################################################
# ec2_root_device: root device will be deleted upon termination
# of the instance by default.
####################################################################

#ec2_root_device: /dev/sda1

####################################################################
# Send email when configuration is complete to 'mailto' address
####################################################################

#relayhost:
#mailto:

####################################################################
# salt_master is the location (dns or ip) of the salt master
# to connect to, e.g.: master.example.com
####################################################################

#salt_master:

####################################################################
# salt_id identifies this salt minion.  If not specified,
# defaults to the fully qualified hostname.
####################################################################

#salt_id:
"""


# if __name__ == '__main__':
#     class Opts(object):
#         def __init__(self, config_dir):
#             self.config_dir = config_dir
#     opts = Opts('.')
#     read_default_config(opts)
