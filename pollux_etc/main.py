#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 29 13:13:28 2017

@author: gkanarek
"""

from __future__ import (print_function, division, absolute_import, with_statement,
                        nested_scopes, generators)

import os

script_dir = os.path.abspath(os.path.dirname(__file__))

import numpy as np
import astropy.units as u
from astropy.table import Table

from syotools import cdbs

from syotools.models import Telescope, Spectropolarimeter, SpectrographicExposure as Exposure
from syotools.interface import SYOTool
from syotools.spectra import SpectralLibrary
from syotools.utils import pre_encode, pre_decode

#We're going to just use the default values for LUVOIR
interface_format = """
Line:
    line_width: 3
    line_alpha: 0.7
Figure:
    plot_height: 400
    plot_width: 800
    tools: "crosshair,pan,reset,save,box_zoom,wheel_zoom,hover"
    toolbar_location: "right"
    background_fill_color: "beige"
    background_fill_alpha: 0.5
    outline_line_color: "black"
Circle:
    fill_color: 'white'
Slider:
    callback_policy: 'mouseup'
Axis:
    axis_label_text_color: 'white'
    major_tick_line_color: 'white'
    minor_tick_line_color: 'white'
    major_label_text_color: 'white'
"""

help_text = """

      <div class="container"> 
          <p>This is the basic ETC for UV spectropolarimetry with POLLUX.<br> 
          <p>The top controls model the source spectrum with various templates, an optional redshift, and magnitude normalization. All template spectra are normalized to the given magnitude in the GALEX FUV band. 
          <p>The top plot shows the input source spectrum in dark red and the "Background Equivalent Flux" for that mode. 
          
          <p>The lower panel shows the signal-to-noise ratio for the selected observing mode/channel, aperture, and exposure time. 
          <p>For any questions regarding this tool please email simona.lombardo@lam.fr
      </div>
"""

#establish simtools dir
if 'LUVOIR_SIMTOOLS_DIR' not in os.environ:
    fdir = os.path.abspath(__file__)
    basedir = os.path.abspath(os.path.join(fdir, '..'))
    os.environ['LUVOIR_SIMTOOLS_DIR'] = basedir

class POLLUX_ETC(SYOTool):
    
    tool_prefix = "pollux"
    
    save_models = ["telescope", "camera", "spectrograph", "spectropolarimeter", "exposure"]
    save_params = {"redshift": None, #slider value
                   "renorm_magnitude": None, #slider value
                   "exptime": None, #slider value
                   "grating": ("spectropolarimeter", "mode"), #drop-down selection
                   "aperture": ("telescope", "aperture"), #slider value
                   "spectrum_type": ("exposure", "sed_id"), #drop-down selection
                   "user_prefix": None}
    
    save_dir = os.path.join(os.environ['LUVOIR_SIMTOOLS_DIR'],'saves')
    
    #must include this to set defaults before the interface is constructed
    tool_defaults = {'redshift': pre_encode(0.0 * u.dimensionless_unscaled),
                     'renorm_magnitude': pre_encode(21.0 * u.mag('AB')),
                     'exptime': pre_encode(1.0 * u.hour),
                     'grating': "NUV_POL",
                     'aperture': pre_encode(15.0 * u.m),
                     'spectrum_type': 'qso'}
    
    def tool_preinit(self):
        """
        Pre-initialize any required attributes for the interface.
        """
        #initialize engine objects
        self.telescope = Telescope(temperature=pre_encode(280.0*u.K))
        self.spectrograph = Spectropolarimeter()
        self.exposure = Exposure()
        self.telescope.add_spectrograph(self.spectrograph)
        self.spectrograph.add_exposure(self.exposure)
        
        #set interface variables
        self.templates = ['o5v','hr1886','alplyr','alpcmi','g2v',
                          'gamdra','mdwarf', 'mdwarf2','ctts2','g191b2b',
                          'gd71', 'gd153','qso', 's99','orion', 'nodust',
                          'ebv6', 'syfrt1','syfrt2','liner','flam']

        self.template_options = [SpectralLibrary[t] for t in self.templates]
        self.help_text = help_text
        self.gratings = self.spectrograph.modes
        self.grating_options = [self.spectrograph.descriptions[g] for g in self.gratings]
        self.dl_filename = ""
        #set default input values
        self.update_exposure()
        
        #Formatting & interface stuff:
        self.format_string = interface_format
        self.interface_file = os.path.join(script_dir, "interface.yaml")
        
        #For saving calculations
        self.current_savefile = ""
        self.overwrite_save = False
        
    tool_postinit = None
    
    def update_exposure(self):
        """
        Update the exposure's parameters and recalculate everything.
        """
        #We turn off calculation at the beginning so we can update everything 
        #at once without recalculating every time we change something
        
        self.exposure.disable()
        
        #Update all the parameters
        self.telescope.aperture = self.aperture
        self.spectrograph.mode = self.grating
        self.exposure.exptime = pre_decode(self.exptime)
        self.exposure.redshift = pre_decode(self.redshift)
        self.exposure.sed_id = self.spectrum_type
        self.exposure.renorm_sed(pre_decode(self.renorm_magnitude), 
                                 bandpass='galex,fuv')
        #Now we turn calculations back on and recalculate
        self.exposure.enable()
        
        #Set the spectrum template
        self.spectrum_template = pre_decode(self.exposure.sed)
    
    @property
    def template_wave(self):
        """
        Easy SED wavelength access for the Bokeh widgets.
        """
        return self.exposure.recover('sed').wave
    
    @property
    def template_flux(self):
        """
        Easy SED flux access for the Bokeh widgets.
        """
        sed = self.exposure.recover('sed')
        wave = sed.wave * u.Unit(sed.waveunits.name)
        if sed.fluxunits.name == "abmag":
            funit = u.ABmag
        elif sed.fluxunits.name == "photlam":
            funit = u.ph / u.s / u.cm**2 / u.AA
        else:
            funit = u.Unit(sed.fluxunits.name)
        flux = (sed.flux * funit).to(u.erg / u.s / u.cm**2 / u.AA, 
                equivalencies=u.spectral_density(wave))
        return flux.value
    
    @property
    def background_wave(self):
        """
        Easy instrument wavelength access for the Bokeh widgets.
        """
        bwave = self.spectrograph.recover('wave').to(u.AA)
        return bwave.value
    
    @property
    def background_flux(self):
        """
        Easy instrument background flux access for the Bokeh widgets.
        """
        bef = self.spectrograph.recover('bef').to(u.erg / u.s / u.cm**2 / u.AA)
        return bef.value
    
    @property
    def _snr(self):
        return np.nan_to_num(self.exposure.recover('snr').value)
        
    
    def controller(self, attr, old, new):
        """
        Callback to recalculate everything for the figures whenever an input's
        value is changed
        """
        
        #Grab values from the inputs
        self.exptime = pre_encode(self.refs["exp_slider"].value * u.hour)
        self.renorm_magnitude = pre_encode(self.refs["mag_slider"].value * u.mag('AB'))
        self.redshift = pre_encode(self.refs["red_slider"].value)
        self.aperture = pre_encode(self.refs["ap_slider"].value * u.m)
        temp = self.template_options.index(self.refs["template_select"].value)
        self.spectrum_type = self.templates[temp]
        grat = self.grating_options.index(self.refs["grating_select"].value)
        self.grating = self.gratings[grat]
                
        #update the exposure and grab all our relevant values.
        self.update_exposure()
        
        snr = self._snr #SNR at bwave
        bwave, bflux = self.background_wave, self.background_flux
        twave, tflux = self.template_wave, self.template_flux
                
        self.refs["flux_yrange"].start = 0.
        self.refs["flux_yrange"].end = 1.5 * tflux.max()
        #self.refs["flux_xrange"].start = min(bwave.min(), twave.min())
        #self.refs["flux_xrange"].end = max(bwave.max(), twave.max())
        self.refs["snr_yrange"].start = 0.
        self.refs["snr_yrange"].end = 1.5 * snr.max()
        #self.refs["snr_xrange"].start = min(bwave.min(), twave.min())
        #self.refs["snr_xrange"].end = max(bwave.max(), twave.max())
        
        self.refs["snr_source"].data = {'y': snr, 'x': bwave}
        self.refs["spectrum_template"].data = {'x': twave, 'y': tflux}
        self.refs["instrument_background"].data = {'x':bwave, 'y':bflux}
        
        self.refs["red_slider"].start = self.exposure.zmin
        self.refs["red_slider"].end = self.exposure.zmax
        
    
    def dl_change_filename(self, attr, old, new):
        self.dl_filename = self.refs["dl_textinput"].value
        self.refs["dl_format_button_group"].active = None
    
    def dl_execute(self, *arg):
        which_format = self.refs["dl_format_button_group"].active
        ext = ['.txt', '.fits'][which_format]
        fmt = ['ascii', 'fits'][which_format]
        outfile = self.dl_filename + ext
        self.refs["dl_linkbox"].text = "Please wait..."
        twave = self.template_wave
        swave = self.background_wave
        snr = self._snr
        out_snr = np.interp(twave, swave, snr, left=0., right=0.)
        out_table = Table([twave, self.template_flux, out_snr],
                         names=('wave','flux','sn'))
        out_table.write(outfile, format=fmt, overwrite=True)
        os.system('gzip -f ' + outfile)
        os.system('cp -rp ' + outfile + '.gz /home/jtastro/jt-astro.science/outputs')
        out_msg = "Your file is <a href='http://jt-astro.science/outputs/{0}.gz'>{0}.gz</a>. "
        self.refs["dl_linkbox"].text = out_msg.format(outfile)

POLLUX_ETC()
