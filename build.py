#!/usr/bin/env python

import argparse
import subprocess
import os

parser = argparse.ArgumentParser(description='Package binary builder')

parser.add_argument('-p', '--package', required=True, choices=['binutils',
'coreutils', 'findutils'], dest = 'package', help='the package to be built')
parser.add_argument('-v', '--version', dest='version', default='', help='package version')
parser.add_argument('-o', '--out-dir', dest='out_dir', help='output binary directory')
parser.add_argument('-O', '--optimization', type=int,
        dest='optimization', help='compiler optimization')

info = {}
info['binutils'] = ['binutils-%s.tar.gz', '2.24',
                    'http://ftp.gnu.org/gnu/binutils/binutils-%s.tar.gz',
                    '-xzf', '-Wno-error=deprecated-declarations']
info['coreutils'] = ['coreutils-%s.tar.xz', '8.23',
                     'http://ftp.gnu.org/gnu/coreutils/coreutils-%s.tar.xz',
                     '-xf', '']
info['findutils'] = ['findutils-%s.tar.gz', '4.4.2',
                     'http://ftp.gnu.org/pub/gnu/findutils/findutils-%s.tar.gz',
                     '-xzf', '']

def build(package, version, optimization=0, out_dir=os.path.join(os.getcwd(),
'bin')):
    if version == '':
        name, version, url, untar_arg, extra = info[package]
    else:
        name, _, url, untar_arg, extra = info[package]
    url = url % version
    name = name % version
    untar_dir = "%s-%s" % (package, version)
    flag = '\"-gdwarf-4 -O%d -m32 %s\"' % (optimization, extra)
    prefix = '/tmp/%s' % untar_dir

    print "Downloading package from %s..." % url
    subprocess.call(['wget', url])

    print "Uncompress package %s..." % name
    subprocess.call(['tar', untar_arg, name])

    os.chdir(untar_dir)

    cmd = ['CFLAGS=%s' % flag, 'CXXFLAGS=%s' % flag, './configure',
            '--prefix=%s' % prefix]
    cmd_str = ' '.join(cmd)
    subprocess.call(cmd_str, shell=True)

    # For coreutils, one might need to reinstall libselinux by:
    # apt-get install libselinux1-dev:i386
    subprocess.call(['make'])
    subprocess.call(['make', 'install'])

    bin_dir = os.path.join(prefix, 'bin')
    if os.path.exists(out_dir):
        print 'Warning: output directory "%s" exists, append binaries into the directory.' % out_dir
        cmd = ['cp', "%s/*" % bin_dir, "%s/." % out_dir]
    else:
        cmd = ['mv', bin_dir, out_dir]
    cmd_str = ' '.join(cmd)
    subprocess.call(cmd_str, shell=True)

if __name__ == '__main__':
    args = parser.parse_args()
    build(args.package, args.version)
