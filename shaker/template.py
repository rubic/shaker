#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Handle the templates to configure user-data.
"""
import os
import re
from jinja2 import Environment
from jinja2 import FileSystemLoader

from shaker import __version__

import shaker.log
LOG = shaker.log.getLogger(__name__)

CLOUD_INIT_PREFIX = 'cloud-init'
USER_SCRIPT_PREFIX = 'user-script'


class UserData(object):
    def __init__(self, config):
        self.config = config
        self.config.update({'version': __version__})
        self.template_dir = self.get_template_dir(self.config['config_dir'])
        self.env = self.get_jinja_env()
        minion_template = re.sub('\n\n+', '\n\n', self.render_template('minion_template', default_contents=MINION_TEMPLATE))
        self.config['rendered_minion_template'] = minion_template
        self.user_script = re.sub('\n\n+', '\n\n', self.render_template('user_data_template', default_contents=USER_SCRIPT))
        self.cloud_init = re.sub('\n\n+', '\n\n', self.render_template('cloud_init_template', default_contents=CLOUD_INIT))

    def get_jinja_env(self):
        ## Using '/' in loader allows to check for absolute paths.
        loader = FileSystemLoader([os.getcwd(), self.template_dir, '/'])
        env = Environment(loader=loader)
        return env

    def render_template(self, template_arg, default_contents=None):
        """
        Retrieve rendered template text from file.
        """
        prefixes = {
            'cloud_init_template': 'cloud-init',
            'user_data_template': 'user-script',
            'minion_template': 'minion-template'
        }
        prefix = prefixes[template_arg]

        if self.config[template_arg] == None:
            template_name = "%s.%s" % (prefix, __version__)
            template_path = os.path.join(self.template_dir, template_name)
            ## Create from default if it doesn't exist.
            if not os.path.isfile(template_path):
                template_file = open(template_path, 'w')
                template_file.write(default_contents)
                template_file.close()
        else:
            template_name = self.config[template_arg]

        return self.env.get_template(template_name).render(self.config)

    def get_template_dir(self, config_dir):
        """Return the template directory name, creating the
        directory if absent (and populating with boilerplate).
        """
        template_dir = os.path.join(config_dir, 'templates')
        if not os.path.isdir(template_dir):
            os.makedirs(template_dir)
        return template_dir


CLOUD_INIT = """#cloud-config
# Shaker version: {{ version }}
{% if salt_master %}
{% if not ec2_distro in ['lucid', 'maverick', 'natty'] %}
apt_sources:
  - source: "ppa:saltstack/salt"

apt_upgrade: true
{% endif %}
{% endif %}

{% if ssh_import %}
ssh_import_id: [{{ ssh_import }}]
{% endif %}

{% if hostname %}
hostname: {{ hostname }}
{% if domain %}
fqdn: {{ hostname }}.{{ domain }}
{% endif %}
{% endif %}
"""

USER_SCRIPT = """#!/bin/sh
# Shaker version: {{ version }}
{% if timezone %}
# set timezone
echo "{{ timezone }}" | tee /etc/timezone
dpkg-reconfigure --frontend noninteractive tzdata
restart cron
{% endif %}

{% if domain and hostname %}
sed -i "s/127.0.0.1 ubuntu/127.0.0.1 localhost {{ hostname }}.{{ domain }} {{ hostname }}/" /etc/hosts
# temp work-around for cloudinit bug: https://bugs.launchpad.net/cloud-init/
echo "127.0.0.1 localhost {{ hostname }}.{{ domain }} {{ hostname }}" >> /etc/hosts
{% elif hostname %}
  hostname: {{ hostname }}
{% endif %}

{% if ssh_port and ssh_port != '22' %}
# change ssh port 22 to non-standard port and restart sshd
sed -i "s/^Port 22$/Port {{ ssh_port }}/" /etc/ssh/sshd_config
/etc/init.d/ssh restart
{% endif %}

{% if sudouser %}
# create new user with sudo privileges
useradd -m -s /bin/bash {{ sudouser }}
{% if ssh_import %}cp -rp /home/ubuntu/.ssh /home/{{ sudouser }}/.ssh
chown -R {{ sudouser }}:{{ sudouser }} /home/{{ sudouser }}/.ssh
{% endif %}
echo "{{ sudouser }} ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers
{% endif %}

{% if size and root_device %}
# resize the filesystem to use specified space
resize2fs {{ root_device }}
{% endif %}

{% if salt_master %}
# Install salt-minion and run as daemon

{% if ec2_distro in ['lucid', 'maverick'] %}
aptitude -y install python-software-properties && add-apt-repository ppa:chris-lea/libpgm && add-apt-repository ppa:chris-lea/zeromq && add-apt-repository ppa:saltstack/salt && aptitude update
{% endif %}

apt-get -y install salt-minion

cat > /etc/salt/minion <<EOF
{{ rendered_minion_template }}
EOF

service salt-minion restart
{% endif %}
"""


MINION_TEMPLATE = """master: {{ salt_master }}

#master_port: 4506

# The user to run salt
#user: root

# The root directory prepended to these options: pki_dir, cachedir, log_file.
#root_dir: /

# The directory to store the pki information in
#pki_dir: /etc/salt/pki

# Explicitly declare the id for this minion to use, if left commented the id
# will be the hostname as returned by the python call: socket.getfqdn()
# Since salt uses detached ids it is possible to run multiple minions on the
# same machine but with different ids, this can be useful for salt compute
# clusters.
{% if salt_id %}
id: {{ salt_id }}
{% else %}
#id:
{% endif %}

# Append a domain to a hostname in the event that it does not exist.  This is
# usefule for systems where socket.getfqdn() does not actually result in a
# FQDN (for instance, Solaris).
#append_domain:

# If the the connection to the server is interrupted, the minion will
# attempt to reconnect. sub_timeout allows you to control the rate
# of reconnection attempts (in seconds). To disable reconnects, set
# this value to 0.
#sub_timeout: 60

# Where cache data goes
#cachedir: /var/cache/salt

# The minion can locally cache the return data from jobs sent to it, this
# can be a good way to keep track of jobs the minion has executed
# (on the minion side). By default this feature is disabled, to enable
# set cache_jobs to True
#cache_jobs: False

# When waiting for a master to accept the minion's public key, salt will
# continuously attempt to reconnect until successful. This is the time, in
# seconds, between those reconnection attempts.
#acceptance_wait_time = 10

# When healing a dns_check is run, this is to make sure that the originally
# resolved dns has not changed, if this is something that does not happen in
# your environment then set this value to False.
#dns_check: True


#####   Minion module management     #####
##########################################
# Disable specific modules. This allows the admin to limit the level of
# access the master has to the minion
#disable_modules: [cmd,test]
#disable_returners: []
#
# Modules can be loaded from arbitrary paths. This enables the easy deployment
# of third party modules. Modules for returners and minions can be loaded.
# Specify a list of extra directories to search for minion modules and
# returners. These paths must be fully qualified!
#module_dirs: []
#returner_dirs: []
#states_dirs: []
#render_dirs: []
#
# A module provider can be statically overwritten or extended for the minion
# via the providers option, in this case the default module will be
# overwritten by the specified module. In this example the pkg module will
# be provided by the yumpkg5 module instead of the system default.
#
# providers:
#   pkg: yumpkg5
#
# Enable Cython modules searching and loading. (Default: False)
#cython_enable: False

#####    State Management Settings    #####
###########################################
# The state management system executes all of the state templates on the minion
# to enable more granular control of system state management. The type of
# template and serialization used for state management needs to be configured
# on the minion, the default renderer is yaml_jinja. This is a yaml file
# rendered from a jinja template, the available options are:
# yaml_jinja
# yaml_mako
# json_jinja
# json_mako
#
#renderer: yaml_jinja
#
# state_verbose allows for the data returned from the minion to be more
# verbose. Normaly only states that fail or states that have changes are
# returned, but setting state_verbose to True will return all states that
# were checked
#state_verbose: False
#
# autoload_dynamic_modules Turns on automatic loading of modules found in the
# environments on the master. This is turned on by default, to turn of
# autoloading modules when states run set this value to False
#autoload_dynamic_modules: True
#
# clean_dynamic_modules keeps the dynamic modules on the minion in sync with
# the dynamic modules on the master, this means that if a dynamic module is
# not on the master it will be deleted from the minion. By default this is
# enabled and can be disabled by changing this value to False
#clean_dynamic_modules: True
#
# Normally the minion is not isolated to any single environment on the master
# when running states, but the environment can be isolated on the minion side
# by statically setting it. Remember that the recommended way to manage
# environments is to issolate via the top file.
#environment: None
#
# If using the local file directory, then the state top file name needs to be
# defined, by default this is top.sls.
#state_top: top.sls

#####     File Directory Settings    #####
##########################################
# The Salt Minion can redirect all file server operations to a local directory,
# this allows for the same state tree that is on the master to be used if
# coppied completely onto the minion. This is a literal copy of the settings on
# the master but used to reference a local directory on the minion.

# Set the file client, the client defaults to looking on the master server for
# files, but can be directed to look at the local file directory setting
# defined below by setting it to local.
#file_client: remote

# The file directory works on environments passed to the minion, each environment
# can have multiple root directories, the subdirectories in the multiple file
# roots cannot match, otherwise the downloaded files will not be able to be
# reliably ensured. A base environment is required to house the top file.
# Example:
# file_roots:
#   base:
#     - /srv/salt/
#   dev:
#     - /srv/salt/dev/services
#     - /srv/salt/dev/states
#   prod:
#     - /srv/salt/prod/services
#     - /srv/salt/prod/states
#
# Default:
#file_roots:
#  base:
#    - /srv/salt

# The hash_type is the hash to use when discovering the hash of a file in
# the minion directory, the default is md5, but sha1, sha224, sha256, sha384
# and sha512 are also supported.
#hash_type: md5

# The Salt pillar is searched for locally if file_client is set to local. If
# this is the case, and pillar data is defined, then the pillar_roots need to
# also be configured on the minion:
#pillar_roots:
#  base:
#    - /srv/pillar

######        Security settings       #####
###########################################
# Enable "open mode", this mode still maintains encryption, but turns off
# authentication, this is only intended for highly secure environments or for
# the situation where your keys end up in a bad state. If you run in open mode
# you do so at your own risk!
#open_mode: False


######         Thread settings        #####
###########################################
# Disable multiprocessing support, by default when a minion receives a
# publication a new process is spawned and the command is executed therein.
#multiprocessing: True

######         Logging settings       #####
###########################################
# The location of the minion log file
#log_file: /var/log/salt/minion
#
# The level of messages to send to the log file.
# One of 'info', 'quiet', 'critical', 'error', 'debug', 'warning'.
# Default: 'warning'
#log_level: warning
#
# Logger levels can be used to tweak specific loggers logging levels.
# For example, if you want to have the salt library at the 'warning' level,
# but you still wish to have 'salt.modules' at the 'debug' level:
#   log_granular_levels: {
#     'salt': 'warning',
#     'salt.modules': 'debug'
#   }
#
#log_granular_levels: {}

######      Module configuration      #####
###########################################
# Salt allows for modules to be passed arbitrary configuration data, any data
# passed here in valid yaml format will be passed on to the salt minion modules
# for use. It is STRONGLY recommended that a naming convention be used in which
# the module name is followed by a . and then the value. Also, all top level
# data must be applied via the yaml dict construct, some examples:
#
# A simple value for the test module:
#test.foo: foo
#
# A list for the test module:
#test.bar: [baz,quo]
#
# A dict for the test module:
#test.baz: {spam: sausage, cheese: bread}"""