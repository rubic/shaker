#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
Select the AMI from specified distro

>>> distro = 'ubuntu'
>>> profile = {'ec2_zone': 'us-west-1a'}
>>> get_ami(distro, profile)
'ami-3f94ca7a'

>>> distro = 'natty'
>>> get_ami(distro, profile)
'ami-43580406'

>>> distro = 'squeeze'
>>> profile['ec2_architecture'] = 'x86_64'
>>> get_ami(distro, profile)
'ami-75287b30'
"""

import yaml

import shaker.log
LOG = shaker.log.getLogger(__name__)

def get_ami(distro, profile):
    """Return an AMI ID matching the distro.
    """
    y = yaml.load(EBSImages)
    try:
        region = profile['ec2_zone'][:-1]
        architecture = profile.get('ec2_architecture', 'i386')
        release = y['release'].get(distro) or distro
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
  ubuntu: oneiric
  debian: squeeze

ubuntu:
  oneiric:
    ap-northeast-1:
      i386: ami-e0fd4be1
      x86_64: ami-e2fd4be3
    ap-southeast-1:
      i386: ami-58cc890a
      x86_64: ami-5ecc890c
    eu-west-1:
      i386: ami-0fe3dc7b
      x86_64: ami-09e3dc7d
    sa-east-1:
      i386: ami-d220ffcf
      x86_64: ami-cc20ffd1
    us-east-1:
      i386: ami-6ba27502
      x86_64: ami-6fa27506
    us-west-1:
      i386: ami-3f94ca7a
      x86_64: ami-c594ca80
    us-west-2:
      i386: ami-e4b03dd4
      x86_64: ami-e6b03dd6
  natty:
    ap-northeast-1:
      x86_64: ami-02b10503
      i386: ami-00b10501
    ap-southeast-1:
      i386: ami-06255f54
      x86_64: ami-04255f56
    eu-west-1:
      i386: ami-a4f7c5d0
      x86_64: ami-a6f7c5d2
    us-east-1:
      i386: ami-e358958a
      x86_64: ami-fd589594
    us-west-1:
      i386: ami-43580406
      x86_64: ami-4d580408
    us-west-2:
      i386: ami-18f97428
      x86_64: ami-1af9742a
  maverick:
    ap-northeast-1:
      i386: ami-dab400db
      x86_64: ami-dcb400dd
    ap-southeast-1:
      i386: ami-58215b0a
      x86_64: ami-5e215b0c
    eu-west-1:
      i386: ami-020f3d76
      x86_64: ami-0e0f3d7a
    sa-east-1:
      i386: ami-6235ea7f
      x86_64: ami-9c35ea81
    us-east-1:
      i386: ami-f333fe9a
      x86_64: ami-cf33fea6
    us-west-1:
      i386: ami-21237f64
      x86_64: ami-23237f66
    us-west-2:
      x86_64: ami-06f97436
      i386: ami-04f97434
  lucid:
    ap-northeast-1:
      i386: ami-1ae6501b
      x86_64: ami-36e65037
    ap-southeast-1:
      i386: ami-d8c98c8a
      x86_64: ami-c0c98c92
    eu-west-1:
      i386: ami-95dde2e1
      x86_64: ami-81dde2f5
    sa-east-1:
      i386: ami-6a5f8077
      x86_64: ami-645f8079
    us-east-1:
      i386: ami-71dc0b18
      x86_64: ami-55dc0b3c
    us-west-1:
      i386: ami-9991cfdc
      x86_64: ami-a191cfe4
    us-west-2:
      i386: ami-8cb33ebc
      x86_64: ami-8eb33ebe

debian:
  squeeze:
    us-east-1:
      i386: ami-1212ef7b
      x86_64: ami-e00df089
    us-west-1:
      i386: ami-77287b32
      x86_64: ami-75287b30
    us-west-2:
      i386: ami-fcf27fcc
      x86_64: ami-8ef27fbe
    eu-west-1:
      i386: ami-e1013695
      x86_64: ami-0f01367b
    ap-northeast-1:
      i386: ami-3ccc663d
      x86_64: ami-5acc665b
    ap-southeast-1:
      i386: ami-b02d54e2
      x86_64: ami-da2d5488
    sa-east-1:
      i386: ami-d427f8c9
      x86_64: ami-3826f925
"""

if __name__ == "__main__":
    import doctest
    doctest.testmod()
