#!/usr/bin/env python
#
# This file is part of RendezvousSim. RendezvousSim is free software: you can
# redistribute it and/or modify it under the terms of the GNU General Public
# License as published by the Free Software Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright 2014 Andre Puschmann <andre.puschmann@tu-ilmenau.de>

import subprocess

i_value = 1000
c_range = range(5,101,5)

print "#alg\tM\tG\tnum_it\tnum_ok\tnum_nok\tTTRmin\tTTRmean\tTTRmax\tTTRstd\tbw\tacdp\ttheta"
    
for c_value in c_range:
    subprocess.call(["./rendezvoussim2.py",
                                "-c %d" % c_value,
                                "-a random,ex,js",
                                "-i %d" % i_value,
                                "-m", "symmetric",
                                "-q",
                                "-n 2"])
