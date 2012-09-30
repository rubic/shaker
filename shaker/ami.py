#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Select the AMI from specified distro

>>> profile = {'ec2_zone': 'us-west-1a'}
>>> get_ami(profile)
'ami-d50c2890'

>>> release = 'lucid'
>>> get_ami(profile, release)
'ami-b988acfc'

>>> profile['ec2_architecture'] = 'x86_64'
>>> get_ami(profile, release)
'ami-bb88acfe'
"""

import yaml

import shaker.log
LOG = shaker.log.getLogger(__name__)

DEFAULT_RELEASE = 'precise'

def get_ami(profile, release=None):
    """Return an AMI ID matching the distro.
    """
    y = yaml.load(EBSImages)
    if not release:
        release = profile.get('ubuntu_release') or DEFAULT_RELEASE
    try:
        region = profile['ec2_zone'][:-1]
        architecture = profile.get('ec2_architecture', 'i386')
        for distro in y['release']:
            if release in y[distro]:
                return y[distro][release][region][architecture]
    except KeyError:
        pass
    except IndexError:
        pass
    return None

# EBSImages to be treated as (and eventually packaged) a yaml file.

EBSImages = """# Amazon EC2 AMIs - EBS Images
release:
  ubuntu: precise

ubuntu:
  precise:
    ap-northeast-1:
      x86_64: ami-c047fac1
      i386: ami-bc47fabd
    ap-southeast-1:
      x86_64: ami-eadb9ab8
      i386: ami-e4db9ab6
    eu-west-1:
      x86_64: ami-db595faf
      i386: ami-d1595fa5
    sa-east-1:
      x86_64: ami-2e845d33
      i386: ami-32845d2f
    us-east-1:
      x86_64: ami-137bcf7a
      i386: ami-057bcf6c
    us-west-1:
      x86_64: ami-d70c2892
      i386: ami-d50c2890
    us-west-2:
      x86_64: ami-1cdd532c
      i386: ami-1add532a
  oneiric:
    ap-northeast-1:
      x86_64: ami-9405b995
      i386: ami-9205b993
    ap-southeast-1:
      x86_64: ami-a86424fa
      i386: ami-aa6424f8
    eu-west-1:
      x86_64: ami-3dcacb49
      i386: ami-33cacb47
    sa-east-1:
      x86_64: ami-00f22b1d
      i386: ami-06f22b1b
    us-east-1:
      x86_64: ami-cdc072a4
      i386: ami-cbc072a2
    us-west-1:
      x86_64: ami-fb5176be
      i386: ami-ff5176ba
    us-west-2:
      x86_64: ami-b47af484
      i386: ami-b27af482
  natty:
    ap-northeast-1:
      x86_64: ami-6c47f56d
      i386: ami-6a47f56b
    ap-southeast-1:
      x86_64: ami-5a5e1f08
      i386: ami-545e1f06
    eu-west-1:
      x86_64: ami-e9bfbb9d
      i386: ami-efbfbb9b
    sa-east-1:
      x86_64: ami-404b955d
      i386: ami-464b955b
    us-east-1:
      x86_64: ami-699f3600
      i386: ami-9f9c35f6
    us-west-1:
      x86_64: ami-1dd0f558
      i386: ami-13d0f556
    us-west-2:
      x86_64: ami-6449c654
      i386: ami-6249c652
  maverick:
    ap-northeast-1:
      x86_64: ami-741dac75
      i386: ami-721dac73
    ap-southeast-1:
      x86_64: ami-0e8acd5c
      i386: ami-0a8acd58
    eu-west-1:
      x86_64: ami-c57942b1
      i386: ami-db7942af
    sa-east-1:
      x86_64: ami-10a9770d
      i386: ami-16a9770b
    us-east-1:
      x86_64: ami-d78f57be
      i386: ami-d38f57ba
    us-west-1:
      x86_64: ami-3b154e7e
      i386: ami-39154e7c
    us-west-2:
      x86_64: ami-64fd7154
      i386: ami-62fd7152
  lucid:
    ap-northeast-1:
      x86_64: ami-8876ca89
      i386: ami-8676ca87
    ap-southeast-1:
      x86_64: ami-903575c2
      i386: ami-923575c0
    eu-west-1:
      x86_64: ami-5d4a4b29
      i386: ami-534a4b27
    sa-east-1:
      x86_64: ami-6ac91077
      i386: ami-68c91075
    us-east-1:
      x86_64: ami-c7b202ae
      i386: ami-c5b202ac
    us-west-1:
      x86_64: ami-bb88acfe
      i386: ami-b988acfc
    us-west-2:
      x86_64: ami-1a4fc12a
      i386: ami-184fc128
"""

if __name__ == "__main__":
    import doctest
    doctest.testmod()
