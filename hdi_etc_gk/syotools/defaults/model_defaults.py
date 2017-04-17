#!/usr/bin/env python
"""
Created on Sat Oct 15 10:59:16 2016

@author: gkanarek, tumlinson
"""
from __future__ import (print_function, division, absolute_import, with_statement,
                        nested_scopes, generators)

#pathlib not supported in python 2
try:
    from pathlib import Path
    use_pathlib = True
except ImportError:
    import os
    use_pathlib = False

import astropy.units as units
import astropy.io.ascii as asc #to read .dat files
import numpy as np

# We use LUVOIR prelim values as defaults for a telescope
default_telescope = {'name': 'LUVOIR',
                     'aperture': 10. * units.m,
                     'temperature': 270. * units.K,
                     'ota_emissivity': 0.09 * units.dimensionless_unscaled,
                     'diff_limit_wavelength': 500. * units.nm}

#Again, prelim LUVOIR camera properties
default_camera = {'name': 'HDI',
                  'pivotwave': np.array([155., 228., 360., 440., 550., 640., 
                                         790., 1260., 1600., 2220.]) * units.nm,
                  'bandnames': ['FUV', 'NUV', 'U','B','V','R','I', 
                                'J', 'H', 'K'],
                  'channels': [([0,1], 2), ([2, 3, 4, 5, 6], 2), ([7, 8, 9], 7)],
                  'ab_zeropoint':  np.array([35548., 24166., 15305., 12523., 
                                             10018., 8609., 6975., 4373., 
                                             3444., 2482.]) * (units.photon / units.s / units.cm**2 / units.nm),
                  'total_qe': np.array([0.1, 0.1, 0.15, 0.45, 0.6, 0.6, 0.6, 
                                        0.6, 0.6, 0.6]) * units.electron / units.ph, #* units.dimensionless_unscaled,
                  'ap_corr': np.full(10, 1., dtype=float) * units.dimensionless_unscaled,
                  'bandpass_r': np.full(10, 5., dtype=float) * units.dimensionless_unscaled,
                  'dark_current': np.array([0.0005, 0.0005, 0.001, 0.001, 
                                            0.001, 0.001, 0.001, 0.002, 0.002, 
                                            0.002]) * (units.electron / units.s / units.pixel),
                  'detector_rn': np.array([3., 3., 3., 3., 3., 3., 3., 4., 
                                           4., 4.]) * (units.electron / units.pixel)}

#LUVOIR Multi-Object Spectrograph

#Load data from ascii table file (need a better method? maybe a FITS table?)
if use_pathlib:
    spec_default_path = str(Path('data') / 'LUMOS_vals.dat')
else:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    spec_default_path = os.path.join(current_dir, '..', 'data', 'LUMOS_vals.dat')
spec_default = asc.read(spec_default_path)
 
default_spectrograph = {'name': 'LUMOS',
                        'modes': {'G120M': 'Med_Res_BEF', 
                                  'G150M': 'Med_Res_BEF', 
                                  'G180M': 'Med_Res_BEF', 
                                  'G155L': 'Low_Res_BEF', 
                                  'G145LL': 'LL_Mode_BEF'},
                        'befs': {mode: spec_default[mode+'_BEF'] * (units.erg / units.s / units.cm**3 / units.sr) 
                                       for mode in ['Med_Res', 'Low_Res', 'LL_mode']},
                        'Rs': {'G120M': 30000., 
                               'G150M': 30000., 
                               'G180M': 30000., 
                               'G155L': 5000., 
                               'G145LL': 500.},
                        'ranges': {'G120M': np.array([1000., 1425.]) * units.AA, 
                                   'G150M': np.array([1225., 1600.]) * units.AA,  
                                   'G180M': np.array([1550., 1900.]) * units.AA, 
                                   'G155L': np.array([1000., 2000.]) * units.AA, 
                                   'G145LL': np.array([900., 1425.]) * units.AA},
                        'mode': 'G150M',
                        'wave': spec_default['Wave'] * units.A,
                        'aeff': spec_default['A_eff'] * units.m**2}

#Placeholder for default coronagraph

default_coronagraph = {}
