#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 18 14:10:45 2016

@author: gkanarek
"""

from __future__ import (print_function, division, absolute_import, with_statement,
                        nested_scopes, generators)

import pysynphot as pys
import astropy.io.ascii as asc
from pathlib import Path
import os

pysyn_base = os.environ['PYSYN_CDBS']

def load_txtfile(spec):
    fname = spec['file']
    band = spec.get('band', 'johnson,v')
    path = Path(fname[0])
    for f in fname[1:]:
        path = path / f
    abspath = str(path.resolve())
    tab = asc.read(abspath, names=['wave','flux']) 
    sp = pys.ArraySpectrum(wave=tab['wave'], flux=tab['flux'], waveunits='Angstrom', fluxunits='flam')
    sp = sp.renorm(30., 'abmag', pys.ObsBandpass(band))
    return sp

def load_pysfits(spec):
    fname = spec['file']
    band = spec.get('band', 'johnson,v')
    path = Path(fname[0])
    for f in fname[1:]:
        path = path / f
    abspath = str(path.resolve())
    sp = pys.FileSpectrum(abspath)
    sp = sp.renorm(30., 'abmag', pys.ObsBandpass(band))
    return sp

specs = {'ctts': {'desc': 'Classical T-Tauri Star', 
                  'file': ['data', 'CTTS_etc_d140pc_101116.txt']},
         'mdwarf': {'desc': 'M1 Dwarf', 
                    'file': ['data', 'dM1_etc_d5pc_101116.txt']},
         's99': {'desc': '10 Myr Starburst', 
                 'file': ['data', '10Myr_Starburst_nodust.dat']},
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
                        'file': [pysyn_base, 'grid', 'etc_models', 
                                 'el_cww_fuv_001.fits']},
         'sbc': {'desc': 'Sbc Galaxy', 
                 'file': [pysyn_base, 'grid', 'etc_models', 
                          'sbc_cb2004a_001.fits']},
         'starburst': {'desc': 'Starburst Galaxy',
                       'file': [pysyn_base, 'grid', 'etc_models', 
                                'sb1_kinney_fuv_001.fits']},
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