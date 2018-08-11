#!/usr/bin/env python2
"""
Created on Tue Feb 14 14:39:33 2017

@author: gkanarek
"""

from __future__ import (print_function, division, absolute_import, with_statement,
                        nested_scopes, generators)

import os
from decimal import Decimal

script_dir = os.path.abspath(os.path.dirname(__file__))

import astropy.units as u
import numpy as np

import holoviews as hv
import pandas
from colorcet import cm
import param

from syotools import cdbs
from syotools.models import Telescope, Camera, PhotometricExposure as Exposure
from syotools.interface import SYOTool
from syotools.utils import pre_encode, pre_decode

#We're going to just use the default values for LUVOIR
interface_format = """
Quad:
    fill_color: 'white'
    fill_alpha: 0.8
    line_alpha: 0.0
HVFigure:
    height: 800
    width: 400
    background_fill_alpha: 1.0
    min_border_left: 0
    min_border_right: 10
    outline_line_color: 'white'
Slider:
    callback_policy: 'mouseup'
Axis:
    axis_line_width: 0
    axis_line_color: 'white'
    visible: False
"""

help_text = """
        <left> 
        <p> This tool illustrates color magnitudes for LUVOIR and other telescopes like it. For now, the "color" is F814W and F606W, and the "magnitude" is F814W. 
        <p> In the "Stars" tab you can set the age, metallcity, distance, and apparent surface brightness of the model population. The tool 
            generates a sample of 10,000 stars with the specified parameters and displays the resulting CMD. 
        <p> In the "Exposure" tab you can set the telescope aperture, exposure time (per band), and the S/N of the floating label at right. 
        <p> The underlying CMDs are drawn from Charlie Conroy's FSPS code, using a simple stellar population with a Chabrier IMF. 
            The blue magnitude numbers at right are the apparent magnitudes in F814W at the distance given in the slider. The apparent magnitude 
            corresponding to the selected distance is given in light blue, and the computed photometric S/N is given in red. You can tune the 
            telescope, exposure, and desired S/N to estimate depths for photometric limits. For the default population (Age = 10 Gyr, solar metallicity, 
            D = 1 Mpc, and AB = 20 / sq. arcsec, S/N = 10 is achieved at AB = 30.9 in 1 hour per band. S/N = 100 is obtained at F814W = 27.6 ABmag in 1 hour. 
            These values are reachable in the no-crowding limit. 
        <p> CMDs are often needed in crowding-limited regions, so this tool estimates the number of stars per square arcsecond to derive crowding 
	    limits independently of the photometric limits. The number of stars per square arcsecond at which "good" photometry can be obtained 
	    is scaled by aperture as 10 * (D/2.4)^2 from the PHAT data of Dalcanton et al. At AB = 22 mag / arcsec^2, the crowding limit is ~390 stars 
	    per arcsec^2 and lies at about AB 30.2 for the population mentioned above. 
        <p> Note that in this beta version of the tool, the noise in the CMD is not scaled for each exposure, and so is illustrative only. 
            The magnitudes and S/N ratios are computed directly from the LUVOIR HDI ETC. 
        </left> 
"""

#establish simtools dir
if 'LUVOIR_SIMTOOLS_DIR' not in os.environ:
    fdir = os.path.abspath(__file__)
    basedir = os.path.abspath(os.path.join(fdir, '../..'))
    os.environ['LUVOIR_SIMTOOLS_DIR'] = basedir
else:
    basedir = os.environ['LUVOIR_SIMTOOLS_DIR']

class ColormapPicker(hv.streams.Stream):                      # set up the colormap picker 
    colormap=param.ObjectSelector(default=cm["kbc"], objects=[cm[k] for k in cm.keys() if not '_' in k])

class CMD(SYOTool):
    
    tool_prefix = "cmd"
    
    save_models = ["telescope", "camera", "exposure"]
    
    save_params = {"exptime": None, #slider value                       #NOT YET UPDATED
                   "snratio": None, #slider value
                   "age": None, #slider value
                   "crowding": None, #slider value
                   "distance": None, #slider value,
                   "metallicity": None, #slider value
                   "noise": None, #slider value
                   "spectrum_type": ("exposure", "sed_id"), 
                   "aperture": ("telescope", "aperture"),
                   "user_prefix": None}
    
    save_dir = os.path.join(os.environ['LUVOIR_SIMTOOLS_DIR'],'saves')
    
    #must include this to set defaults before the interface is constructed
    tool_defaults = {'exptime': pre_encode(3600.0 * u.s),
                     'snratio': pre_encode(30.0 * u.electron**0.5),
                     'age': pre_encode(u.Dex(10.0 * u.Gyr)),
                     'crowding': pre_encode(20.0 * u.dimensionless_unscaled), #u.ABmag / u.arcsec**2),
                     'distance': pre_encode(1.0 * u.Mpc),
                     'metallicity': pre_encode(u.Dex(0.0)),
                     'noise': pre_encode(500.0 * u.dimensionless_unscaled),
                     'aperture': pre_encode(15.0 * u.m),
                     'spectrum_type': 'fab'
                     }
    
    verbose = True
    
    def tool_preinit(self):
        """
        Pre-initialize any required attributes for the interface.
        """
        #set up holoviews & load data for datashader
        #note that right now the data is read from a pickle, not loaded separately;
        #I'm leaving load_dataset.py in the directory, but it's not used currently
        self.dataframe = pandas.read_pickle(os.path.join(basedir,'data','cmd_frame_large_no_noise.pkl'))
        self.cmap_picker = ColormapPicker(rename={'colormap': 'cmap'}, name='')
        
        #initialize engine objects
        self.telescope = Telescope()
        self.camera = Camera()
        self.exposure = Exposure()
        self.telescope.add_camera(self.camera)
        self.camera.add_exposure(self.exposure)
        
        #set interface variables
        self.help_text = help_text
        
        #Formatting & interface stuff:
        self.format_string = interface_format
        self.interface_file = os.path.join(script_dir, "interface.yaml")
        
        #For saving calculations
        self.current_savefile = ""
        self.overwrite_save = False
        
    def tool_postinit(self):
        #update default exposure based on tool_defaults
        self.update_exposure_params()

    #Calculation methods
    
    @staticmethod
    def add_noise(new_frame, noise_scale): 
        rmag = new_frame.rmag
        gmag = new_frame.gmag
        noise_basis = 10. / 10.**((30.+rmag) / 5.) # mind the 10! 
        r_noise = np.random.normal(0.0, noise_scale, np.size(rmag)) * noise_basis 
        g_noise = np.random.normal(0.0, noise_scale, np.size(rmag)) * noise_basis 
        new_frame.rmag = rmag + r_noise 
        new_frame.gmag = gmag + g_noise 
        new_frame.grcolor = np.clip(rmag - gmag, a_min=-1.2, a_max=4.2)
        return new_frame
    
    def select_dataframe(self, metallicity, age):
        selection = lambda frame: (frame.metalindex == metallicity) & (frame.ageindex == age)
        return self.dataframe.loc[selection]
    
    def select_stars(self, obj, age, metallicity, noise): # received "obj" of type "Points" and "age" of type ordinary float 
        #"obj" incoming is the points object 
        if self.verbose:
            print("age / metallicity / noise inside select_stars", age, metallicity, noise) 
        new_frame = self.select_dataframe(metallicity, age)
        noise_frame = self.add_noise(new_frame, float(noise)) 
        cmd_points = hv.Points(noise_frame, kdims=['grcolor', 'rmag']) 
        return cmd_points 
    
    @property
    def _derived_snrs(self):
        new_snrs = np.zeros(5, dtype=float)
        mags = self.refs["cmd_mag_source"].data["mags"]
        for m, mag in enumerate(mags):
            self.exposure.renorm_sed(mag * u.ABmag)
            new_snrs[m] = self.exposure.recover('snr')[4].value
            
        return new_snrs
    
    @property
    def _derived_snrs_labels(self):
        return self._derived_snrs.astype('|S4')
    
    def crowding_limit(self, crowding_apparent_magnitude, distance):
        """
        Calculate the crowding limit.
        """
        aperture = pre_decode(self.aperture)
        
        g_solar = 4.487
        stars_per_arcsec_limit = 10. * (aperture / 2.4) ** 2 # (JD1) 
    
        distmod = 5. * np.log10((distance + 1e-5) * 1e6) - 5. #why this fudge?
        
        g = np.array(-self.dataframe.gmag) # absolute magnitude in the g band - the -1 corrects for the sign flip in load_datasets (for plotting) 
        g.sort() 				# now sorted from brightest to faintest in terms of absolute g magnitude 
        luminosity = 10.**(-0.4 * (g - g_solar)) 
        total_luminosity_in_lsun = np.sum(luminosity) 
        number_of_stars = np.full_like(g, 1.0)     # initial number of stars in each "bin" - a list of 10,000 stars 
    
        total_absolute_magnitude = -2.5 * np.log10(total_luminosity_in_lsun) + g_solar 
        apparent_brightness_at_this_distance = total_absolute_magnitude + distmod 
    
        scale_factor = 10.**(-0.4*(crowding_apparent_magnitude - apparent_brightness_at_this_distance)) 
        cumulative_number_of_stars = np.cumsum(scale_factor * number_of_stars) # the cumulative run of luminosity in Lsun 
        
        crowding_limit = np.interp(stars_per_arcsec_limit.value, cumulative_number_of_stars, g) 
        
        return crowding_limit 
    
    #Control methods
    
    def quantize_slider(self, ref, precision, minval, step):
        """
        A utility function for quantizing the value of a slider.
        """
        val = Decimal(self.refs[ref].value).quantize(Decimal(precision))
        return int(((val - Decimal(minval)) / Decimal(step)).to_integral_exact())
        
    
    def age_slider_update(self):
        """
        Send an event to the age stream.
        """
        new_age = self.quantize_slider("age_slider", '0.01', '5.5', '0.05')
        self.refs["age_stream"].event(age=new_age) 
        if self.verbose:
            print("Age selected by slider = {}".format(new_age))
        
    def metallicity_slider_update(self):
        """
        Send an event to the metallicity stream. Using Decimal to handle 
        quantization.
        """
        new_metallicity = self.quantize_slider("metallicity_slider", '0.1', 
                                               '-2.0', '0.5')
        self.refs["metallicity_stream"].event(metallicity=new_metallicity)
        if self.verbose:
            print("Metallicity selected by slider = {}".format(new_metallicity))
    
    def noise_slider_update(self): 
        """
        Send an event to the noise stream. This slider is in steps of 50, so
        we can just quantize with int() instead of using Decimal.
        """
        ival = int(self.refs["noise_slider"].value)
        if self.verbose:
            print("Inside noise_slider, will scale to: {}".format(ival))
        self.refs["noise_stream"].event(noise=ival)
    
    def distance_slider_update(self):
        """
        Update the magnitude label source for the new distance.
        """
        val = self.refs["distance_slider"].value
        distmod = 5. * np.log10((val + 1e-5) * 1e6) - 5.
        new_mags = distmod+np.array([10., 5., 0., -5., -10.])
        mlsource = self.refs['cmd_mag_source']
        mlsource.data['mags'] = new_mags
        mlsource.data['text'] = new_mags.astype('|S4')
        
    def crowding_slider_update(self):
        """
        Update the crowding from the slider input.
        """        
        crowding_mag = self.refs["crowding_slider"].value
        distance = self.refs["distance_slider"].value
    
        nstars_per_arcsec = int(10. * (self.refs['ap_slider'].value / 2.4)**2) 
        crowding_limit = self.crowding_limit(crowding_mag, distance)
        confsource = self.refs["cmd_conf_source"]
        confsource.data = {'top':[-crowding_limit], 
                           'textx':[-0.8], 'texty':[-crowding_limit - 0.2], 
                           'text':['Crowding: ({} stars / sq. arsec)'.format(nstars_per_arcsec)]}
        
    def update_exposure_params(self):
        """
        Update the exposure parameters.
        """
        
        new_aper = self.refs["ap_slider"].value * u.m
        new_expt = (self.refs["exp_slider"].value * u.h).to(u.s)
        new_snr = self.refs["snr_slider"].value * u.electron ** 0.5
        
        self.aperture = pre_encode(new_aper)
        self.exptime = pre_encode(new_expt)
        self.snratio = pre_encode(new_snr)
        
        self.telescope.aperture = self.aperture
        
    
    def exposure_update(self):        
        """
        Update the exposure when sliders are updated.
        """
        self.update_exposure_params()
        
        self.exposure.unknown = 'snr'
        self.exposure.exptime = pre_decode(self.exptime)
        
        new_snrs = self._derived_snrs
        etcsource = self.refs["cmd_etc_source"]
        mlsource = self.refs["cmd_mag_source"]
        
        etcsource.data = {"mags": mlsource.data["mags"],
                          "snr": new_snrs,
                          "snr_label": new_snrs.astype('|S4'),
                          'x': np.full(5, 3.2).tolist(),
                          'y': np.arange(-10.4, 10., 5., dtype=float).tolist()}

        if self.verbose:
            print("mag_values in exposure_update: {}".format(etcsource.data['y']))
            print("new_snrs in exposure_update: {}".format(etcsource.data['snr']))
        
        noise_scale_factor = int(10000. / new_snrs[1]) # divide an number by the S/N at AB = 5 absolute - set up to make it come out right 
        self.refs["noise_stream"].event(noise=int(noise_scale_factor))
        
    def sn_slider_update(self):  
        """
        Update exposure when SNR slider is changed.
        """
        new_sn = pre_decode(self.snratio)
        new_expt = pre_decode(self.exptime)
        #new_sn = self.refs["snr_slider"].value
        #new_expt = self.refs["exp_slider"].value
        if self.verbose:
            print("calling sn_updater with sn = {} and exptime {}".format(new_sn, new_expt)) 
        
        self.exposure.unknown = "magnitude"
        self.exposure.exptime = new_expt #pre_decode(self.exptime)
        self.exposure.snr = new_sn #pre_decode(self.snratio)
        
        vmag = self.exposure.recover('magnitude')[4].value
        distance = pre_decode(self.distance)
        distmod = 5. * np.log10((distance.value + 1e-5) * 1e6) - 5. 
        
        lmsource = self.refs["cmd_lim_source"]
        lmsource.data = {'mags':[distmod - vmag - 0.4],
                         'maglabel':["{:4.1f}".format(vmag)],
                         'sn':["{}".format(new_sn.value)],
                         'x_mag':[3.8], 'x_sn':[3.2]} # the 0.4 is just for display purposes (text alignment)
    
    def changed_value(self, ref, param, unit):
        new_val = self.refs[ref].value
        if unit is not None:
            new_val = new_val * unit
        if ref == "exp_slider":
            new_val = pre_encode(new_val.to(u.s))
        elif ref == "age_slider":
            new_val = pre_encode(u.Dex(10. ** new_val * u.Gyr))
        elif ref == "metallicity_slider":
            new_val = pre_encode(u.Dex(new_val))
        else:
            new_val = pre_encode(new_val)
        if ref == "crowding_slider":
            print(param, getattr(self, param), new_val)
        if getattr(self, param) != new_val:
            setattr(self, param, new_val)
            return True
        return False
    
    def controller(self, attr, old, new):
        """
        Master controller callback. Instead of having a bunch of different
        callbacks, instead we're going to track which things have changed,
        and then call the individual update methods that are required.
        """
        
        #Grab values from the inputs, tracking which have changed
        
        params = {'exp': ('exp_slider', 'exptime', u.hour),
                  'age': ('age_slider', 'age', None),
                  'snr': ('snr_slider', 'snratio', u.electron**0.5),
                  'crowd': ('crowding_slider', 'crowding', u.dimensionless_unscaled), # u.ABmag / u.arcsec**2),
                  'dist': ('distance_slider', 'distance', u.Mpc),
                  'metal': ('metallicity_slider', 'metallicity', None),
                  'noise': ('noise_slider', 'noise', u.dimensionless_unscaled),
                  'aper': ('ap_slider', 'aperture', u.m)}
        
        updated = set([par for par, args in params.items() if self.changed_value(*args)])
        
        #Call the requisite update methods
        if not updated.isdisjoint({'dist', 'aper', 'exp'}):
            self.exposure_update()
        if not updated.isdisjoint({'dist', 'aper', 'exp', 'crowd'}):
            self.crowding_slider_update()
        if not updated.isdisjoint({'dist', 'aper', 'exp', 'snr'}):
            self.sn_slider_update()
        if 'noise' in updated:
            self.noise_slider_update()
        if 'dist' in updated:
            self.distance_slider_update()
        if 'metal' in updated:
            self.metallicity_slider_update()
        if 'age' in updated:
            self.age_slider_update()

        #Now, all of the plot updates should be handled by stream events, I think...
    
    #NONE OF THESE MATTER UNTIL SAVE/LOAD IS ADDED
    
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
            "the ID {}".format(self.current_savefile)
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
        
    

CMD()

