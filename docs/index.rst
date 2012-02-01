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



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

