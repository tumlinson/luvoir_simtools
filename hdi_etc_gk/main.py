#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 14 14:39:33 2017

@author: gkanarek
"""

from __future__ import (print_function, division, absolute_import, with_statement,
                        nested_scopes, generators)

import os#; os.environ['PYSYN_CDBS'] = os.path.expanduser("~/cdbs")

script_dir = os.path.abspath(os.path.dirname(__file__))

import numpy as np
import astropy.units as u

from syotools import cdbs

from pysynphot import ObsBandpass

from syotools.models import Telescope, Camera
from syotools.interface import SYOTool
from syotools.spectra import SpectralLibrary

#We're going to just use the default values for LUVOIR
interface_format = """
Line:
    line_width: 3
    line_alpha: 1.0
Figure:
    plot_height: 400
    plot_width: 800
    tools: "crosshair,pan,reset,save,box_zoom,wheel_zoom"
    toolbar_location: "right"
    background_fill_color: "beige"
    background_fill_alpha: 0.5
Circle:
    fill_color: 'white'
Slider:
    callback_policy: 'mouseup'
"""

help_text = """

      <div class="container"> 
        <div class="col-lg-6">
         <p>This is the basic ETC for photometry in multiband images. Choose your telescope aperture, exposure time, and magnitude normalization. The normalization is done in the V band (550 nm). 
        <p> Given an aperture and magnitude, choose the exposure time that reaches your desired S/N.  
        <p>To obtain limiting magnitudes given exposure time, set that time and then tune the magnitude to reach your desired limiting S/N.</p>
        </div>
        <div class="col-lg-6">
          <p>The details of these calculations are <a href="http://jt-astro.science/luvoir_simtools/hdi_etc/SNR_equation.pdf" target="_blank"> here</a>. We assume that the pixel size in each band critically samples the telescope's diffraction limited PSF at the shortest wavelength in that channel. Thermal backgrounds are included for T = 280 K, which substantially affects the K band.</p>
        </div>
      </div>
"""

hover_tooltip = """
        <div>
            <div>
                <span style="font-size: 17px; font-weight: bold; color: #696">@desc band</span>
            </div>
            <div>
                <span style="font-size: 15px; font-weight: bold; color: #696">S/N = </span>
                <span style="font-size: 15px; font-weight: bold; color: #696;">@y</span>
            </div>
        </div>
"""

class HDI_ETC(SYOTool):
    
    def tool_preinit(self):
        """
        Pre-initialize any required attributes for the interface.
        """
        #initialize engine objects
        self.telescope = Telescope()
        self.camera = Camera()
        self.telescope.add_camera(self.camera)
        
        #set interface variables
        self.templates = ['fab', 'bb', 'o5v', 'b5v', 'g2v', 'm2v', 'orion',
                          'elliptical', 'sbc', 'starburst', 'ngc1068']
        self.template_options = [SpectralLibrary[t] for t in self.templates]
        self.help_text = help_text
        self.hover_tooltip = hover_tooltip
        
        #set defaults
        self.exptime = 1.0 * u.hour
        self.renorm_magnitude = 30.0 * u.mag('AB')
        self.aperture = 12.0 * u.m
        self.spectrum_type = 'fab'
        self.update_sed()
        
        #Formatting & interface stuff:
        self.format_string = interface_format
        self.interface_file = os.path.join(script_dir, "interface.yaml")
        
    #No post-initialization required
    tool_postinit = None
    
    def controller(self, attr, old, new):
        #Grab values from the inputs
        self.exptime = self.refs["exp_slider"].value * u.hour
        self.renorm_magnitude = self.refs["mag_slider"].value * u.mag('AB')
        self.aperture = self.refs["ap_slider"].value * u.m
        temp = self.template_options.index(self.refs["template_select"].value)
        self.spectrum_type = self.templates[temp]
        
        #Update the template SED based on new values
        self.update_sed()
        
        snr = self.snr

        #Update the y ranges & data
        self.refs["snr_figure"].y_range.start = 0
        self.refs["snr_figure"].y_range.end = 1.3 * max(snr.value.max(), 5.)
        self.refs["sed_figure"].y_range.start = self.spectrum_template.flux.min() + 5.
        self.refs["sed_figure"].y_range.end = self.spectrum_template.flux.min() - 5.
        self.refs["source_blue"].data = {'x': self.camera.pivotwave[2:-3], 
                                         'y': snr[2:-3],
                                         'desc': self.camera.bandnames[2:-3]}
        self.refs["source_orange"].data = {'x': self.camera.pivotwave[:2], 
                                           'y': snr[:2],
                                           'desc': self.camera.bandnames[:2]}
        self.refs["source_red"].data = {'x': self.camera.pivotwave[-3:], 
                                        'y': snr[-3:],
                                        'desc': self.camera.bandnames[-3:]}
        self.refs["spectrum_template"].data = {'x': self.template_wave,
                                               'y': self.template_flux}
        
    def update_sed(self):
        spectrum = SpectralLibrary.get(self.spectrum_type)
        band = ObsBandpass('johnson,v')
        band.convert('nm')
        new_spectrum = spectrum.renorm((self.renorm_magnitude + 2.5*u.mag('AB')).value,
                                       'abmag', band)
        new_spectrum.convert('nm')
        new_spectrum.convert('abmag')
        sed = new_spectrum.sample(self.camera.pivotwave.value)
        
        if np.count_nonzero(~np.isfinite(new_spectrum.flux)):
            print("Infinite values!")

        self.spectrum_template = new_spectrum
        self.sed = sed * u.mag('AB')
        
    @property
    def snr(self):
        self.telescope.aperture = self.aperture
        out = self.camera.signal_to_noise(self.exptime, 3, self.sed, verbose=False)
        return out
    
    @property
    def template_wave(self):
        return np.asarray(self.spectrum_template.wave)
    
    @property
    def template_flux(self):
        return np.asarray(self.spectrum_template.flux)


HDI_ETC()

