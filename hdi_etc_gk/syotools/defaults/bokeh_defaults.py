#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 18 15:02:03 2016

@author: gkanarek
"""

from __future__ import (print_function, division, absolute_import, with_statement,
                        nested_scopes, generators)

from pathlib import Path
import numpy as np
import astropy.units as u


planetary_model_path = (Path('data') / 'earth_quadrature_radiance_refl.dat').resolve()
planetary_model = np.loadtxt(str(planetary_model_path), skiprows=8)

default_coronograph = {'int_time': 20.0 * u.h,
                       'phase_angle': 90. * u.deg, 
                       'phase_func': 1.,
                       'r_planet': 1.0 * u.R_earth,
                       'semimajor': 1.0 * u.au,
                       't_eff': 5780. * u.K,
                       'r_star': 1. * u.R_sun,
                       'd_system': 10. * u.pc,
                       'n_exoz': 1.,
                       'wave': planetary_model[:,0] * u.um,
                       'radiance': planetary_model[:,1] * (u.W / u.m**2 / u.um / u.sr),
                       'sol_flux': planetary_model[:,2] * (u.W / u.m**2 / u.um)}