#!/usr/bin/env python
import sys
from BeautifulSoup import BeautifulSoup

"""
Utility program to list AMIs for ubuntu cloud server releases:

$ UDISTRO=precise; curl -o $UDISTRO.txt http://cloud-images.ubuntu.com/releases/$UDISTRO/release/
$ echo "  $UDISTRO:"; ./ubuntu_cloud_images.py $UDISTRO.txt
"""

Arch = {'32-bit': 'i386', '64-bit': 'x86_64'}

def ami_tuples(data):
    """Return ubuntu server release info as a list of named tuples
    """
    soup = BeautifulSoup(data)
    table = soup.find('table')
    rows = table.findAll('tr')
    headings = [td.find(text=True).strip() for td in rows[0].findAll('td')]
    ami_list = []

    for row in rows[1:]:
        r = [p.text for p in [td for td in row.findAll('td')]]
        ami = dict(zip(headings, r))
        if not ami['root store'] == 'ebs':
            continue
        ami['architecture'] = Arch[ami['arch']]
        ami['id'] = ami['ami'].replace('Launch', '')
        ami_list.append(ami)
    return ami_list

def ami_yaml(data):
    yaml_list = []
    region = None
    for ami in ami_tuples(data):
        if not ami['Region'] == region:
            yaml_list.append('    {0}:'.format(ami['Region']))
        yaml_list.append('      {0}: {1}'.format(ami['architecture'], ami['id']))
        region = ami['Region']
    return yaml_list

if __name__ == '__main__':
    datafile = sys.argv[1]
    data = open(datafile).read()
    for y in ami_yaml(data):
        print y
