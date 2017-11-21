#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 20 12:22:25 2017

@author: gkanarek

Run from the command line:
    $ python test_syotools_models
Or, to save the output in a file:
    $ python test_syotools_models > model_test.log
"""
from __future__ import print_function

from syotools.models import Exposure, Camera, Telescope
from pprint import pprint

print("\n\n==Instantiating models==")
print("(setting verbose = True)\n")

e, c, t = Exposure(), Camera(), Telescope()
t.add_camera(c)
c.add_exposure(e)
e.verbose = True

print("\n\n==Parameter values (aka defaults):==")
print("\n=TELESCOPE=\n")
pprint(t.encode(), indent=2)
print("\n=CAMERA=\n")
pprint(c.encode(), indent=2)
print("\n=EXPOSURE=\n")
pprint(e.encode(), indent=2)

print("\n\n==Setting spectrum to QSO & recalculating==\n")
e.sed_id = 'qso'

print("\n\n==Current unkown: {}==".format(e.unknown))
print("\nSNR: {}".format(e.snr))

print("\n\n==Setting unknown to 'magnitude'==\n")
e.unknown = "magnitude"
print("\nMagnitude: {}".format(e.magnitude))

print("\n\n==Setting unknown to 'exptime'==\n")
e.unknown = "exptime"
print("\nExptime: {}".format(e.exptime))