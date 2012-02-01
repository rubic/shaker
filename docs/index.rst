.. shaker documentation master file, created by
   sphinx-quickstart on Tue Jan 31 20:33:49 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Shaker: A salt minion factory for EC2 instances
===============================================

Release

Shaker is BSD-New Licensed command-line application to launch Salt
minions as Amazon EC2 instances.

Salt is a powerful remote execution manager that can be used to
administer servers in a fast and efficient way.

Running an Amazon EC2 instance as a Salt minion is fairly simple.
Also tedious, if you need to launch minions often.  Shaker bridges
the gap between launching an EC2 instance and bootstrapping it as
a Salt minion.

Shaker is invoked from the command line:

::

    $ shaker --distro ubuntu --master salt.example.com


Contents:

.. toctree::
   :maxdepth: 2

Examples:

    $ shaker --dry-run --distro=ubuntu

    Chooses an AMI based on defaults.  Dumps the "dry run" user data
    to the screen.


    $ shaker --distro=ubuntu  --master yourmaster.example.com

    Started Instance: i-9175d8f4

    To access: ssh ubuntu@ec2-107-20-93-179.compute-1.amazonaws.com

    To terminate: shaker-terminate i-9175d8f4


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

