============================
Shaker Profile Configuration
============================

Salt minions are usually launched with Shaker specifying a
user-defined profile, which overrides ``default`` values.  A
user-defined profile effectively extends the default, so you may
modify ``default`` with global values, declaring only per-minion
values in the minion profile.

Unless otherwise specified, profiles are located in the
``~/.shaker/profile`` directory.

Salt-Specific Configuration Options
-----------------------------------

``salt_master``
---------------

Default: None

Specify the location of a running Salt master.

.. code-block:: yaml

    salt_master: salt.example.com

``salt_id``
------------

Default: ``hostname``  (fully-qualified)

``salt_id`` identifies this salt minion to the master.  If not
specified, defaults to the fully qualified hostname.

.. code-block:: yaml

    salt_id: moonunit


Host Configuration Options
--------------------------

``hostname``
-------------

Default: (determined by EC2 startup)

The hostname is passed to EC2 initialization, prior to boot-up.
The usual case is to specify hostname and domain because these
values determine the Salt minion ID in the absence of an explicit
``salt_id``.

.. code-block:: yaml

    hostname: igor

``domain``
----------

Default: (assigned by Amazon: amazonaws.com)

The domain name assigned to the instance.

.. code-block:: yaml

    domain: example.com


``timezone``
------------

Default: (UTC, if not specified)

`Timezone <http://en.wikipedia.org/wiki/List_of_tz_database_time_zones>`_
for your instance.

.. code-block:: yaml

    timezone: America/Chicago


``ssh_import``
--------------

Default: None

Import public keys from `launchpad.net <http://launchpad.net>`_.
Only applicable for Ubuntu cloud-init.  User names are
comma-separated, no spaces.

Launchpad provides a free service for
`registering public keys <https://help.launchpad.net/YourAccount/CreatingAnSSHKeyPair>`_
that are assigned to Ubuntu instances, if specified in ``ssh_import``.

.. code-block:: yaml

    ssh_import: jbauer,akoumjian

``sudouser``
------------

Default: None

Install the user with sudo privileges.  If ``sudouser`` is listed
in ``ssh_import``, the public key will be installed from
`launchpad.net <http://launchpad.net>`_.

.. code-block:: yaml

    sudouser: jbauer

``ssh_port``
------------

Default: ``22``

Port enabled to allow ssh connections.  You may specify a
non-standard ssh port, but verify it's open in your
``ec2_security_group``.

.. code-block:: yaml

    ssh_port: 6222


EC2-Specific Configuration Options
----------------------------------

``ec2_zone``
------------

Default: ``us-east-1b``

Specify the
`zone <http://aws.amazon.com/ec2/faqs/#How_isolated_are_Availability_Zones_from_one_another>`_
to start the instance.   The default may be changed in ``~/.shaker/profile/default``.

.. code-block:: yaml

    ec2_zone: us-west-1a


``ec2_instance_type``
---------------------

Default: ``m1.small``

`Amazon EC2 Instance Type <Specify the http://aws.amazon.com/ec2/instance-types/>`_:

 * t1.micro
 * m1.small  (default)
 * m2.xlarge, m2.2xlarge, m2.4xlarge
 * c1.medium, c1.xlarge, cc1.4xlarge, cc2.8xlarge

.. code-block:: yaml

    ec2_instance_type: t1.micro

``ec2_ami_id``
--------------

Default: None

The `AMI <http://aws.amazon.com/amis>`_ id of the image to launch.
Note that AMI's are region-specific, so you must specify the the
appropriate AMI for the specific ``ec2_zone``.  Specifying
``ec2_ami_id`` overrides ``ec2_distro`` below.

.. code-block:: yaml

    ec2_ami_id: ami-6ba27502

``ec2_distro``
--------------

Default: ``ubuntu``

Specify the distribution to launch: *precise*, *oneiric*, *natty*, *maverick*, *lucid*,
or generically, *ubuntu*.

*Note: Only ``oneiric`` is currently guaranteed to work, until the
packaging is back ported.*

*TODO: Add support for Debian, Fedora, etc.*

.. code-block:: yaml

    ec2_distro: oneiric

``ec2_size``
------------

Default: (determined by EC2 startup)

Size of the root partition in gigabytes.  If zero or not specified,
defaults to the instance type.

.. code-block:: yaml

    ec2_size: 20

``ec2_key_name``
----------------

Default: ``default``

Name of the
`key pair <http://docs.amazonwebservices.com/AWSEC2/latest/UserGuide/generating-a-keypair.html>`_
used to create the instance. If not specified and only one key-pair is available, it will be
used.  Otherwise you must disambiguate by specifying the key-pair.

.. code-block:: yaml

    ec2_key_name: rubickey

``ec2_security_group``
----------------------

Default: ``default``

The security group to control port access to the instance (ssh,
http, etc.)  If not specified, use ``default``, which generally
permits port 22 for ssh access.

.. code-block:: yaml

    ec2_security_group: webserver

``ec2_monitoring_enabled``
--------------------------

Default: ``false``

Enable EC2 instance monitoring with
`CloudWatch <http://aws.amazon.com/cloudwatch/>`_

.. code-block:: yaml

    ec2_monitoring_enabled: true

``ec2_root_device``
-------------------

Default: ``/dev/sda1``

Specify the root device name for the instance.

.. code-block:: yaml

    ec2_root_device: /dev/sdh
