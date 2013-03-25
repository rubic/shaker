"""
Build and launch EBS instances as salt minions.
"""
from shaker.version import __version__

import os
import sys
import time
import optparse
import email.mime
from tempfile import TemporaryFile
from M2Crypto import BIO, RSA, m2
import boto
import boto.ec2
from boto.ec2.blockdevicemapping import EBSBlockDeviceType, BlockDeviceMapping
import shaker.log
import shaker.config
import shaker.template
LOG = shaker.log.getLogger(__name__)
RUN_INSTANCE_TIMEOUT = 180  # seconds
DEFAULT_MINION_PKI_DIR = '/etc/salt/pki/master/minions'

InstanceTypes = [
    't1.micro',
    'm1.small',
    'm1.medium',
    'm1.large',
    'm1.xlarge',
    'm2.xlarge',
    'm2.2xlarge',
    'm2.4xlarge',
    'c1.medium',
    'c1.xlarge',
    'cc1.4xlarge',
    'cc2.8xlarge',
    'cg1.4xlarge',
    'hi1.4xlarge',
    ]


class EBSFactory(object):
    """EBSFactory - build and launch EBS salt minions.
    """
    def __init__(self):
        cli, config_dir, profile = self.parse_cli()
        self.profile = shaker.config.user_profile(
            cli,
            config_dir,
            profile)
        self.pki_dir = shaker.config.get_pki_dir(config_dir)
        self.userdata_dir = shaker.config.get_userdata_dir(config_dir)
        self.dry_run = cli.dry_run
        self.write_user_data = cli.write_user_data
        self.minion_pki_dir = cli.minion_pki_dir or DEFAULT_MINION_PKI_DIR
        self.config = dict(self.profile)
        self.config['config_dir'] = config_dir
        self.pre_seed = cli.pre_seed or self.config['pre_seed']
        self.ip_address = cli.ip_address or self.config['ip_address']

    def process(self):
        if self.pre_seed:
            if not self.generate_minion_keys():
                return False
        self.user_data = self.build_mime_multipart()
        if self.write_user_data or (
            self.get_keyname() and not self.pre_seed and not self.dry_run):
            self.write_user_data_to_file()
        self.conn = self.get_connection()
        if not self.conn:
            errmsg = "Unable to establish a connection for: {0}".format(
                self.config['ec2_region'])
            LOG.error(errmsg)
            return False
        if not self.verify_settings():
            return False
        if self.dry_run:
            return True
        if self.pre_seed:
            self.pre_seed_minion()
        self.launch_instance()
        assigned_ip_address = None
        if self.ip_address:
            ip_in_use = self.ip_address_in_use()
            if ip_in_use:
                errmsg = "Unable to assign ip address {0}, " \
                         "already in use with instance {1}".format(
                    self.ip_address, ip_in_use.id)
                LOG.error(errmsg)
            else:
                self.conn.associate_address(self.instance.id, self.ip_address)
                assigned_ip_address = self.ip_address
        if self.config['assign_dns']:
            LOG.info("assign_dns not yet implemented") #XXX Not yet implemented
            self.assign_dns(self.config['assign_dns'])
        self.output_response_to_user(assigned_ip_address)
        return True

    def get_connection(self):
        conn_params = {
            'aws_access_key_id': self.config['ec2_access_key_id'],
            'aws_secret_access_key': self.config['ec2_secret_access_key'],
        }
        try:
            conn = boto.ec2.connect_to_region(self.config['ec2_region'], **conn_params)
        except boto.exception.BotoClientError as e:
            errmsg = "Unable to connect to the region {0}: {1}".format(
                    self.config['ec2_region'], e.reason)
            LOG.error(errmsg)
            conn = None
        return conn

    def launch_instance(self):
        if not self.verify_settings():
            return
        is_instance_store = self.conn.get_all_images(self.config['ec2_ami_id'], filters={'root-device-type': 'instance-store'})
        if is_instance_store:
            block_map = None
        else:
            block_map = BlockDeviceMapping()
            root_device = self.config['ec2_root_device']
            block_map[root_device] = EBSBlockDeviceType()
            if self.config['ec2_size']:
                block_map[root_device].size = self.config['ec2_size']
            block_map[root_device].delete_on_termination = True
        reservation = self.conn.run_instances(
            self.config['ec2_ami_id'],
            key_name=self.config['ec2_key_name'],
            security_groups=self.config['ec2_security_groups'] or [self.config['ec2_security_group']],
            instance_type=self.config['ec2_instance_type'],
            placement=self.config['ec2_zone'],
            placement_group=self.config['ec2_placement_group'],
            monitoring_enabled=self.config['ec2_monitoring_enabled'],
            block_device_map=block_map,
            user_data=self.user_data)
        self.instance = reservation.instances[0]
        secs = RUN_INSTANCE_TIMEOUT
        rest_interval = 5
        while secs and not self.instance.state == 'running':
            time.sleep(rest_interval)
            secs = secs - rest_interval
            try:
                self.instance.update()
            except boto.exception.EC2ResponseError:
                pass
        if secs <= 0:
            errmsg = "run instance {0} failed after {1} seconds".format(
                self.instance.id, RUN_INSTANCE_TIMEOUT)
            LOG.error(errmsg)
        else:
            if self.config['hostname']:
                self.assign_name_tag()

    def output_response_to_user(self, assigned_ip_address):
        msg1 = "Started Instance: {0}\n".format(self.instance.id)
        LOG.info(msg1)
        print msg1
        p = int(self.config['ssh_port'])
        port = str(p) if p and not p == 22 else ''
        ## change user to 'root' for all non-Ubuntu systems
        user = self.config['sudouser'] if self.config['sudouser'] and self.config['ssh_import'] else 'ubuntu'
        address = assigned_ip_address if assigned_ip_address else self.instance.public_dns_name
        # TODO: replace public dns with fqdn, where appropriate
        msg2 = "To access: ssh {0}{1}@{2}\n".format(
            '-p {0} '.format(port) if port else '',
            user,
            address)
        msg3 = "To terminate: shaker-terminate {0}".format(
                   self.instance.id)
        LOG.info(msg2)
        LOG.info(msg3)
        print msg2
        print msg3

    def write_user_data_to_file(self):
        keyname = self.get_keyname()
        if keyname:
            pathname = os.path.join(self.userdata_dir, keyname)
            with open(pathname, 'w') as f:
                f.write('{0}\n'.format(self.user_data))
            LOG.info("user data written to {0}".format(pathname))
        else:
            LOG.error("unable to determine salt_id: specify hostname")

    def pre_seed_minion(self):
        """Pre-seed minion keys, updating /etc/salt/pki/minion
        """
        if not os.access(self.minion_pki_dir, os.W_OK | os.X_OK):
            errmsg = "directory not writeable: {0}".format(self.minion_pki_dir)
            LOG.error(errmsg)
            return False
        keyname = self.get_keyname()
        minionpubkey_pathname = os.path.join(
            self.minion_pki_dir,
            keyname)
        with open(minionpubkey_pathname, 'w') as f:
            f.write(self.public_key)
        return True

    def get_keyname(self):
        if self.config.get('salt_id'):
            keyname = self.config['salt_id']
        elif self.config.get('hostname'):
            if self.config.get('domain'):
                keyname = "{0}.{1}".format(
                    self.config['hostname'],
                    self.config['domain'])
            else:
                keyname = self.config['hostname']
        else:
            keyname = None
        return keyname

    def ip_address_in_use(self):
        """If the ip_address is in use, return associated instance,
        otherwise return None.
        """
        for instances in [r.instances for r in self.conn.get_all_instances()]:
            for i in instances:
                if i.ip_address == self.ip_address and i.state == 'running':
                    return i
        return None

    def generate_minion_keys(self):
        #XXX TODO: Replace M2Crypto with PyCrypto
        # see: https://github.com/saltstack/salt/pull/1112/files
        # generate keys
        keyname = self.get_keyname()
        if not keyname:
            LOG.error("Must specify salt_id or hostname")
            return False
        gen = RSA.gen_key(2048, 1, callback=lambda x,y,z:None)
        pubpath = os.path.join(self.pki_dir,
                               '{0}.pub'.format(keyname))
        gen.save_pub_key(pubpath)
        LOG.info("public key {0}".format(pubpath))
        if self.config.get('save_keys'):
            cumask = os.umask(191)
            gen.save_key(
                os.path.join(
                    self.pki_dir,
                    '{0}.pem'.format(keyname)),
                None)
            os.umask(cumask)
        # public key
        _pub = TemporaryFile()
        bio_pub = BIO.File(_pub)
        m2.rsa_write_pub_key(gen.rsa, bio_pub._ptr())
        _pub.seek(0)
        self.config['public_key'] = self.public_key = _pub.read()
        self.config['formatted_public_key'] = '\n'.join(
            "    {0}".format(k) for k in self.public_key.split('\n'))
        # private key
        _pem = TemporaryFile()
        bio_pem = BIO.File(_pem)
        gen.save_key_bio(bio_pem, None)
        _pem.seek(0)
        self.config['private_key'] = self.private_key = _pem.read()
        self.config['formatted_private_key'] = '\n'.join(
            "    {0}".format(k) for k in self.private_key.split('\n'))
        return True

    def assign_name_tag(self):
        """Assign the 'Name' tag to the instance, but only if it
        isn't already in use.
        """
        tag = self.config['hostname']
        for reservation in self.conn.get_all_instances():
                for i in reservation.instances:
                    if tag == i.tags.get('Name'):
                        return
        self.instance.add_tag('Name', tag)

    def build_mime_multipart(self):
        userData = shaker.template.UserData(self.config)
        outer = email.mime.multipart.MIMEMultipart()
        for content, subtype, filename in [
            (userData.user_script, 'x-shellscript', 'user-script.txt'),
            (userData.cloud_init, 'cloud-config', 'cloud-config.txt'),]:
            msg = email.mime.text.MIMEText(content, _subtype=subtype)
            msg.add_header('Content-Disposition',
                           'attachment',
                           filename=filename)
            outer.attach(msg)
        return outer.as_string()

    def verify_settings(self):
        if not self.config['ec2_ami_id']:
            LOG.error("Missing ec2_ami_id")
            return False
        if not self.config['ec2_key_name']:
            # If no key pair has been specified, just use the first one,
            # if it's the only key pair.  Otherwise the user must specify.
            key_pairs = self.conn.get_all_key_pairs()
            if len(key_pairs) < 1:
                LOG.error("No key pair available for region: {0}" % self.conn)
            elif len(key_pairs) > 1:
                errmsg = "Must specify ec2-key or ec2_key_name: {0}".format(
                    ', '.join([kp.name for kp in key_pairs]))
                LOG.error(errmsg)
                return False
            self.config['ec2_key_name'] = [kp.name for kp in key_pairs][0]
        if self.config['ec2_size']:
            try:
                self.config['ec2_size'] = int(self.config['ec2_size'])
            except ValueError:
                LOG.error("Invalid ec2_size: {0}".format(
                    self.config['ec2_size']))
                return False
        if not self.config['ec2_instance_type'] in InstanceTypes:
            LOG.error("Invalid ec2_instance_type: {0}".format(
                self.config['ec2_instance_type']))
            return False
        return True

    def parse_cli(self):
        parser = optparse.OptionParser(
            usage="%prog [options] profile",
            version="%%prog {0}".format(__version__))
        parser.add_option(
            '-a', '--ami', dest='ec2_ami_id', metavar='AMI',
            help='Build instance from AMI')
        parser.add_option(
            '--release', dest='release',
            metavar='UBUNTU_RELEASE', default='',
            help="Ubuntu release (precise, lucid, etc.)")
        parser.add_option('--ec2-group', dest='ec2_security_group')
        parser.add_option('--ec2-key', dest='ec2_key_name')
        parser.add_option('--ec2-region', dest='ec2_region',
                          help="Region to use: us-east-1, etc.")
        parser.add_option('--ec2-zone', dest='ec2_zone',
                          help="Availability zone to use: us-east-1b, etc.")
        parser.add_option('--instance-type', dest='ec2_instance_type',
                          help="One of t1.micro, m1.small, ...")
        parser.add_option('--placement-group', dest='ec2_placement_group')
        parser.add_option(
            '--config-dir', dest='config_dir',
            help="Configuration directory")
        parser.add_option(
            '--user-data', dest='user_data_template',
            help="User data template file")
        parser.add_option(
            '--cloud-init', dest='cloud_init_template',
            help="cloud-init template file")
        parser.add_option(
            '--minion-template', dest='minion_template',
            help="Minion template file")
        parser.add_option(
            '--dry-run', dest='dry_run',
            action='store_true', default=False,
            help="Log the initialization setup, but don't launch the instance")
        parser.add_option(
            '-m', '--master', dest='salt_master',
            metavar='SALT_MASTER', default='',
            help="Connect salt minion to SALT_MASTER")
        parser.add_option(
            '--hostname', dest='hostname',
            metavar='HOSTNAME', default='',
            help="Assign HOSTNAME to salt minion")
        parser.add_option(
            '--domain', dest='domain',
            metavar='DOMAIN', default='',
            help="Assign DOMAIN name to salt minion")
        parser.add_option(
            '--ip_address', dest='ip_address',
            metavar='IP_ADDRESS', default='',
            help="Assign elastic IP address to salt minion")
        parser.add_option(
            '--preseed', dest='pre_seed',
            action='store_true', default=False,
            help="Pre-seed the minion keys")
        parser.add_option(
            '--save-keys', dest='save_keys',
            action='store_true', default=False,
            help="Save keys locally, including the pre-seeded private key")
        parser.add_option(
            '--minion-pki-dir', dest='minion_pki_dir',
            metavar='PKI_DIR', default=DEFAULT_MINION_PKI_DIR,
            help="Minion PKI_DIR, when pre-seeding minion keys")
        parser.add_option(
            '-w', '--write-user-data', dest='write_user_data',
            action='store_true', default=False,
            help="Write user-data to USERDATA directory (~/.shaker/userdata)")
        import shaker.log
        parser.add_option('-l',
                '--log-level',
                dest='log_level',
                default='info',
                choices=shaker.log.LOG_LEVELS.keys(),
                help='Log level: {0}.  \nDefault: %%default'.format(
                     ', '.join(shaker.log.LOG_LEVELS.keys()))
                )
        (opts, args) = parser.parse_args()
        if len(args) < 1:
            if opts.ec2_ami_id or opts.release:
                profile = None
            else:
                print parser.format_help().strip()
                errmsg = "\nError: Specify shaker profile or EC2 ami or Ubuntu release"
                raise SystemExit(errmsg)
        else:
            profile = args[0]
        import shaker.config
        config_dir = shaker.config.get_config_dir(opts.config_dir)
        shaker.log.start_logger(
            __name__,
            os.path.join(config_dir, 'shaker.log'),
            opts.log_level)
        if opts.ec2_ami_id:
            opts.distro = ''  # mutually exclusive
        else:
            opts.distro = opts.release
        LOG.info("shaker invoked with args: {0}".format(', '.join(sys.argv[1:])))
        return opts, config_dir, profile
