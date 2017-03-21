#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 18 14:10:45 2016

@author: gkanarek
"""

from __future__ import (print_function, division, absolute_import, with_statement,
                        nested_scopes, generators)

import os; os.environ['PYSYN_CDBS'] = os.path.expanduser("~/cdbs")

import pysynphot as pys
import astropy.io.ascii as asc

#pathlib is not supported in python 2
try:
    from pathlib import Path
    use_pathlib = True
except ImportError:
    use_pathlib = False

pysyn_base = os.environ['PYSYN_CDBS']
data_base = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','data'))

def load_txtfile(spec):
    fname = spec['file']
    band = spec.get('band', 'johnson,v')
    if use_pathlib:
        path = Path(fname[0])
        for f in fname[1:]:
            path = path / f
        abspath = str(path.resolve())
    else:
        abspath = os.path.abspath(os.path.join(*fname))
    tab = asc.read(abspath, names=['wave','flux']) 
    sp = pys.ArraySpectrum(wave=tab['wave'], flux=tab['flux'], waveunits='Angstrom', fluxunits='flam')
    sp = sp.renorm(30., 'abmag', pys.ObsBandpass(band))
    sp.convert('abmag')
    sp.convert('nm')
    return sp

def load_pysfits(spec):
    fname = spec['file']
    band = spec.get('band', 'johnson,v')
    if use_pathlib:
        path = Path(fname[0])
        for f in fname[1:]:
            path = path / f
        abspath = str(path.resolve())
    else:
       abspath = os.path.abspath(os.path.join(*fname)) 
    sp = pys.FileSpectrum(abspath)
    sp = sp.renorm(30., 'abmag', pys.ObsBandpass(band))
    sp.convert('abmag')
    sp.convert('nm')
    return sp

specs = {'ctts': {'desc': 'Classical T-Tauri Star', 
                  'file': [data_base, 'CTTS_etc_d140pc_101116.txt'],
                  'band': 'galex,fuv'},
         'mdwarf': {'desc': 'M1 Dwarf', 
                    'file': [data_base, 'dM1_etc_d5pc_101116.txt'],
                    'band': 'galex,fuv'},
         's99': {'desc': '10 Myr Starburst', 
                 'file': [data_base, '10Myr_Starburst_nodust.dat'],
                 'band': 'galex,fuv'},
         'qso': {'desc': 'QSO', 
                 'file': [pysyn_base, 'grid', 'agn', 'qso_template.fits'], 
                 'band': 'galex,fuv'},
         'o5v': {'desc': 'O5V Star', 
                 'file': [pysyn_base, 'grid', 'pickles', 'dat_uvk', 
                          'pickles_uk_1.fits']},
         'g2v': {'desc': 'G2V Star', 
                 'file': [pysyn_base, 'grid', 'pickles', 'dat_uvk', 
                          'pickles_uk_26.fits']},
         'orion': {'desc': 'Orion Nebula', 
                   'file': [pysyn_base, 'grid', 'galactic', 
                            'orion_template.fits']},
         'g191b2b': {'desc': 'G191B2B', 
                     'file': [pysyn_base, 'calspec', 'g191b2b_mod_010.fits']},
         'nodust': {'desc': 'Starburst, No Dust', 
                    'file': [pysyn_base, 'grid', 'kc96', 
                             'starb1_template.fits']},
         'ebv6': {'desc': 'Starburst, E(B-V) = 0.6', 
                  'file': [pysyn_base, 'grid', 'kc96', 
                           'starb6_template.fits']},
         'b5v': {'desc': 'B5V Star', 
                 'file': [pysyn_base, 'grid', 'pickles', 'dat_uvk', 
                          'pickles_uk_6.fits']},
         'm2v': {'desc': 'M2V Star', 
                 'file': [pysyn_base, 'grid', 'pickles', 'dat_uvk', 
                          'pickles_uk_40.fits']},
         'elliptical': {'desc': 'Elliptical Galaxy', 
                        #'file': [pysyn_base, 'grid', 'etc_models', 
                        #         'el_cww_fuv_001.fits']},
                        'file': [pysyn_base, 'grid', 'kc96', 
                                'elliptical_template.fits'],
                        'band': 'galex,fuv'},
         'sbc': {'desc': 'Sbc Galaxy', 
                 #'file': [pysyn_base, 'grid', 'etc_models', 
                 #         'sbc_cb2004a_001.fits']},
                 'file': [pysyn_base, 'grid', 'kc96', 
                          'sc_template.fits'],
                 'band': 'galex,fuv'},
         'starburst': {'desc': 'Starburst Galaxy',
                       #'file': [pysyn_base, 'grid', 'etc_models', 
                       #         'sb1_kinney_fuv_001.fits']},
                       'file': [pysyn_base, 'grid', 'kc96', 
                                'starb1_template.fits'],
                       'band': 'galex,fuv'},
         'ngc1068': {'desc': 'NGC 1068',
                     'file': [pysyn_base, 'grid', 'agn', 
                              'ngc1068_template.fits']}}

default_spectra = {'specs':{}, 'descs':{}}

for (specid, spec) in specs.items():
    default_spectra['descs'][specid] = spec['desc']
    fits = spec['file'][-1].endswith('fits')
    if fits:
        default_spectra['specs'][specid] = load_pysfits(spec)
    else:
        default_spectra['specs'][specid] = load_txtfile(spec)

flatsp = pys.FlatSpectrum(30, fluxunits='abmag') 
flatsp = flatsp.renorm(30., 'abmag', pys.ObsBandpass('johnson,v'))
flatsp.convert('abmag') 
flatsp.convert('nm') 
default_spectra['specs']['fab'] = flatsp
default_spectra['descs']['fab'] = 'Flat (AB)'

bb = pys.BlackBody(5000)
bb.convert('abmag') 
bb.convert('nm') 
default_spectra['specs']['bb'] = bb
default_spectra['descs']['bb'] = 'Blackbody (5000K)'