#!/usr/bin/env python2
"""
Created on Tue Feb 14 14:39:33 2017

@author: gkanarek
"""

from __future__ import (print_function, division, absolute_import, with_statement,
                        nested_scopes, generators)

import os#; os.environ['PYSYN_CDBS'] = os.path.expanduser("~/cdbs")

script_dir = os.path.abspath(os.path.dirname(__file__))

import astropy.units as u

from syotools import cdbs

from syotools.models import Telescope, Camera, PhotometricExposure as Exposure
from syotools.interface import SYOTool
from syotools.spectra import SpectralLibrary
from syotools.utils import pre_encode, pre_decode

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
                <span style="font-size: 15px; font-weight: bold; color: #696">{} = </span>
                <span style="font-size: 15px; font-weight: bold; color: #696;">@y</span>
            </div>
        </div>
"""

#establish simtools dir
if 'LUVOIR_SIMTOOLS_DIR' not in os.environ:
    fdir = os.path.abspath(__file__)
    basedir = os.path.abspath(os.path.join(fdir, '..'))
    os.environ['LUVOIR_SIMTOOLS_DIR'] = basedir

class HDI_ETC(SYOTool):
    
    tool_prefix = "hdi"
    
    save_models = ["telescope", "camera", "exposure"]
    save_params = {"exptime": None, #slider value
                   "snratio": None, #slider value
                   "renorm_magnitude": None, #slider value
                   "spectrum_type": ("exposure", "sed_id"), 
                   "aperture": ("telescope", "aperture"),
                   "user_prefix": None}
    
    save_dir = os.path.join(os.environ['LUVOIR_SIMTOOLS_DIR'],'saves')
    
    #must include this to set defaults before the interface is constructed
    tool_defaults = {'exptime': pre_encode(1.0 * u.hour),
                     'snratio': pre_encode(30.0 * u.electron**0.5),
                     'renorm_magnitude': pre_encode(30.0 * u.mag('AB')),
                     'aperture': pre_encode(12.0 * u.m),
                     'spectrum_type': 'fab'}
    
    def tool_preinit(self):
        """
        Pre-initialize any required attributes for the interface.
        """
        #initialize engine objects
        self.telescope = Telescope()
        self.camera = Camera()
        self.exposure = Exposure()
        self.telescope.add_camera(self.camera)
        self.camera.add_exposure(self.exposure)
        
        #set interface variables
        self.templates = ['fab', 'bb', 'o5v', 'b5v', 'g2v', 'm2v', 'orion',
                          'elliptical', 'sbc', 'starburst', 'ngc1068']
        self.template_options = [SpectralLibrary[t] for t in self.templates]
        self.help_text = help_text
        self.snr_hover_tooltip = hover_tooltip.format("S/N")
        self.mag_hover_tooltip = hover_tooltip.format("Magnitude")
        self.exp_hover_tooltip = hover_tooltip.format("Exptime")
        
        #update default exposure based on tool_defaults
        self.update_exposure()
        
        #Formatting & interface stuff:
        self.format_string = interface_format
        self.interface_file = os.path.join(script_dir, "interface.yaml")
        
        #For saving calculations
        self.current_savefile = ""
        self.overwrite_save = False
        
    def tool_postinit(self):
        """
        Need to disable the SNR slider to start with.
        """
        self.refs["snr_slider"].disabled = True
    
    #Control methods
    def tab_change(self, attr, old, new):
        """
        Whenever tabs are switched:
            - Disable the appropriate input slider(s)
            - Set self.exposure.unknown, if appropriate
        """
        active_tab = new['value'][0]
        all_inputs = ["ap_slider", "exp_slider", "mag_slider", "snr_slider",
                      "template_select"]
        inactive = [("snr_slider",), ("exp_slider",), ("mag_slider",), 
                    ("ap_slider", "exp_slider", "snr_slider")][active_tab]
        for inp in all_inputs:
            self.refs[inp].disabled = inp in inactive
            
        #set the correct exposure unknown:
        if active_tab < 3:
            self.exposure.unknown = ["snr", "exptime", "magnitude"][active_tab]
        
        self.controller(None, None, None)
    
    def controller(self, attr, old, new):
        #Grab values from the inputs
        self.exptime = pre_encode(self.refs["exp_slider"].value * u.hour)
        self.renorm_magnitude = pre_encode(self.refs["mag_slider"].value * u.mag('AB'))
        self.snratio = pre_encode(self.refs["snr_slider"].value * u.electron**0.5)
        self.aperture = pre_encode(self.refs["ap_slider"].value * u.m)
        temp = self.template_options.index(self.refs["template_select"].value)
        self.spectrum_type = self.templates[temp]
        
        self.update_exposure()
        
        snr = self._snr
        mag = self._mag
        exp = self._exp
        pwave = self._pivotwave
        
        #Update the plots' y-range bounds
        self.refs["snr_figure"].y_range.start = 0
        self.refs["snr_figure"].y_range.end = max(1.3 * snr.max(), 5.)
        self.refs["exp_figure"].y_range.start = 0
        self.refs["exp_figure"].y_range.end = max(1.3 * exp.max(), 2.)
        self.refs["mag_figure"].y_range.start = mag.max() + 5.
        self.refs["mag_figure"].y_range.end = mag.min() - 5.
        self.refs["sed_figure"].y_range.start = self.spectrum_template.flux.max() + 5.
        self.refs["sed_figure"].y_range.end = self.spectrum_template.flux.min() - 5.
        
        #Update source data
        self.refs["snr_source_blue"].data = {'x': pwave[2:-3], 
                                             'y': snr[2:-3],
                                             'desc': self.camera.bandnames[2:-3]}
        self.refs["exp_source_blue"].data = {'x': pwave[2:-3], 
                                             'y': exp[2:-3],
                                             'desc': self.camera.bandnames[2:-3]}
        self.refs["mag_source_blue"].data = {'x': pwave[2:-3], 
                                             'y': mag[2:-3],
                                             'desc': self.camera.bandnames[2:-3]}
        self.refs["snr_source_orange"].data = {'x': pwave[:2], 
                                               'y': snr[:2],
                                               'desc': self.camera.bandnames[:2]}
        self.refs["exp_source_orange"].data = {'x': pwave[:2], 
                                               'y': exp[:2],
                                               'desc': self.camera.bandnames[:2]}
        self.refs["mag_source_orange"].data = {'x': pwave[:2], 
                                               'y': mag[:2],
                                               'desc': self.camera.bandnames[:2]}
        self.refs["snr_source_red"].data = {'x': pwave[-3:], 
                                            'y': snr[-3:],
                                            'desc': self.camera.bandnames[-3:]}
        self.refs["exp_source_red"].data = {'x': pwave[-3:], 
                                            'y': exp[-3:],
                                            'desc': self.camera.bandnames[-3:]}
        self.refs["mag_source_red"].data = {'x': pwave[-3:], 
                                            'y': mag[-3:],
                                            'desc': self.camera.bandnames[-3:]}
        self.refs["spectrum_template"].data = {'x': self.template_wave,
                                               'y': self.template_flux}
        
    def update_exposure(self):
        """
        Update the exposure's parameters and recalculate everything.
        """
        #We turn off calculation at the beginning so we can update everything 
        #at once without recalculating every time we change something
        self.exposure.disable() 
        
        #Update all the parameters
        self.exposure.n_exp = 3
        self.exposure.exptime = pre_decode(self.exptime)
        self.exposure.snr = pre_decode(self.snratio)
        self.exposure.sed_id = self.spectrum_type
        self.telescope.aperture = self.aperture
        self.exposure.renorm_sed(pre_decode(self.renorm_magnitude))
        
        #Now we turn calculations back on and recalculate
        self.exposure.enable()
        
        #Set the spectrum template
        self.spectrum_template = pre_decode(self.exposure.sed)
    
    @property
    def template_wave(self):
        return self.exposure.recover('sed').wave
    
    @property
    def template_flux(self):
        return self.exposure.recover('sed').flux

    #Conversions to avoid Bokeh Server trying to serialize Quantities
    @property
    def _pivotwave(self):
        return self.camera.recover('pivotwave').value
    
    @property
    def _snr(self):
        return self.exposure.recover('snr').value
    
    @property
    def _mag(self):
        return self.exposure.recover('magnitude').value
    
    @property
    def _exp(self):
        exp = self.exposure.recover('exptime').to(u.h)
        return exp.value
    
    def update_toggle(self, active):
        if active:
            self.refs["user_prefix"].value = self.user_prefix
            self.refs["user_prefix"].disabled = True
            self.refs["save_button"].disabled = False
            self.overwrite_save = True
        else:
            self.refs["user_prefix"].disabled = False
            self.refs["save_button"].disabled = False
            self.overwrite_save = False
    
    #Save and Load
    def save(self):
        """
        Save the current calculations.
        """
        
        #Check for an existing save file if we're overwriting
        if self.overwrite_save and self.current_savefile:
            self.current_savefile = self.save_file(self.current_savefile, 
                                                   overwrite=True)
        else:
            #Set the user prefix from the bokeh interface
            prefix = self.refs["user_prefix"].value
            if not prefix.isalpha() or len(prefix) < 3:
                self.refs["save_message"].text = "Please include a prefix of at "\
                    "least 3 letters (and no other characters)."
                return
            self.user_prefix = prefix
            #Save the file:
            self.current_savefile = self.save_file()
        
        #Tell the user the filename or the error message.
        if not self.current_savefile:
            self.refs["save_message"].text = "Save unsuccessful; please " \
                "contact the administrators."
            return
        
        self.refs["save_message"].text = "This calculation was saved with " \
            "the ID {}.".format(self.current_savefile)
        self.refs["update_save"].disabled = False
        
    
    def load(self):
        # Get the filename from the bokeh interface
        calcid = self.refs["load_filename"].value
        
        #Load the file
        code = self.load_file(calcid)
        
        if not code: #everything went fine
            #Update the interface
            self.refs["update_save"].disabled = False
            self.current_save = calcid
            self.refs["exp_slider"].value = pre_decode(self.exptime).value
            self.refs["mag_slider"].value = pre_decode(self.renorm_magnitude).value
            self.refs["ap_slider"].value = pre_decode(self.aperture).value
            self.refs["snr_slider"].value = pre_decode(self.snratio).value
            temp = self.templates.index(self.spectrum_type)
            self.refs["template_select"].value = self.template_options[temp]
            self.controller(None, None, None)
            
        errmsg = ["Calculation ID {} loaded successfully.".format(calcid),
                  "Calculation ID {} does not exist, please try again.".format(calcid),
                  "Load unsuccessful; please contact the administrators.",
                  "There was an error restoring the save state; please contact"
                  " the administrators."][code]
        if code == 0 and self.load_mismatch:
            errmsg += "<br><br><b><i>Load Mismatch Warning:</b></i> "\
                      "The saved model parameters did not match the " \
                      "parameter values saved for this tool. Saved " \
                      "model values were given priority."
        self.refs["load_message"].text = errmsg
        
    

HDI_ETC()

