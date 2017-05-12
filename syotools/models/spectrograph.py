#!/usr/bin/env python
"""
Created on Sat Oct 15 16:56:40 2016

@author: gkanarek, tumlinson
"""

from __future__ import (print_function, division, absolute_import, with_statement,
                        nested_scopes, generators)

import numpy as np
import astropy.units as u

from syotools.models.base import PersistentModel
from syotools.defaults import default_spectrograph
from syotools.utils import pre_encode

class Spectrograph(PersistentModel):
    """
    The basic spectrograph class, which provides parameter storage for 
    optimization.
    
    Attributes: #adapted from the original in Telescope.py
        telescope    - the Telescope object associated with the spectrograph
        camera       - the Camera object associated with the spectrograph
    
        name         - name of the spectrograph (string)
        
        modes        - supported observing modes and associated values (dict)
        befs         - blackbody emission functions in erg/s/cm3/sr (dict)
        Rs           - spectral resolution for each mode (dict)
        ranges       - wavelength range for each mode (dict)
        mode         - current observing mode (string)
        wave         - wavelengths in Angstroms (float array)
        aeff         - effective area at given wavelengths [UNITS?] (float array)
        
        _default_model - used by PersistentModel
    """
    
    _default_model = default_spectrograph
    
    name = ''
    modes = {}
    befs = {}
    Rs = {}
    mode = ''
    wave = pre_encode(np.zeros(0, dtype=float) * u.AA)
    aeff = pre_encode(np.zeros(0, dtype=float) * u.dimensionless_unscaled) #don't know units yet

    @property
    def bef(self):
        return self.befs[self.mode]

    @property
    def R(self):
        return self.Rs[self.mode]

    @property
    def delta_lambda(self):
        wave, R = self.recover('wave', 'R')
        return pre_encode(wave / R)
    
    @property
    def lamdba_range(self):
        return self.ranges[self.mode]