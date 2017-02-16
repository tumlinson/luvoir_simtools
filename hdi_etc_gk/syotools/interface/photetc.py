#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 19 14:44:30 2016

@author: gkanarek, tumlinson
"""

from .base import SYOTool
from models import Camera, Telescope

class PhotETC(SYOTool):
    """
    Photometric exposure time calculator (ETC) tool.
    """
    plot_type = ('line', 'circle')
    model_type = ('camera', 'telescope')
    model_vars = {'camera': {'pivotwave': 'Wavelength Bands',
                             'ab_zeropoint': 'Zero-point Flux',
                             'total_qe': 'Quantum Efficiency',
                             'ap_corr': 'Aperture Correction',
                             'bandpass_r': 'Bandpass Resolution',
                             'dark_current': 'Dark Current',
                             'detector_rn': 'Detector Read Noise'},
                  'telescope': {'aperture': 'Aperture Size',
                                'temperature': 'OTA Temperature',
                                'ota_emissivity': 'OTA Emissivity',
                                'diff_limit_wavelength': 'Diffraction Limit'}}
    y_function = ('signal_to_noise',)
    x_input = (('camera','pivotwave'), )
    input_vars = {'magnitude': 'Object SED',
                  'exptime': 'Integration Time',
                  'n_exp': 'Number of Exposures'}

