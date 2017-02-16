#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 14 20:28:51 2016

@author: gkanarek, tumlinson
"""

from __future__ import (print_function, division, absolute_import, with_statement,
                        nested_scopes, generators)
from .base import PersistentModel
from defaults import default_telescope
import astropy.units as u #for unit conversions


class Telescope(PersistentModel):
    """
    The basic telescope class, which provides parameter storage for 
    optimization.
    
    Attributes: #adapted from the original in Telescope.py
        name - The name of the telescope (string)
        aperture - The size of the primary telescope aperture, in meters (float)
        temperature - instrument temperature, in Kelvin (float)
        ota_emissivity - emissivity factor for a TMA (float)
        diff_limit_wavelength - diffraction limit wavelength, in nm (float)
        
        _default_model - used by PersistentModel
        
        cameras - the Camera objects for this telescope
    """
    _default_model = default_telescope
    
    cameras = []
    
    name = ''
    aperture = 0. * u.m
    temperature = 0. * u.K
    ota_emissivity = 0. * u.dimensionless_unscaled
    diff_limit_wavelength = 0. * u.nm
        
    @property
    def diff_limit_arcsec(self):
        """
        Convert the diffraction limit from nm to arcseconds.
        """
        return (1.22 * u.rad * self.diff_limit_wavelength / self.aperture).to(u.arcsec)
    
    def add_camera(self, camera):
        self.cameras.append(camera)
        camera.telescope = self
    
    