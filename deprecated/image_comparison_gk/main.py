# -*- coding: utf-8 -*-
"""
Created on Wed Mar 22 10:59:03 2017

@author: gkanarek
"""

from __future__ import (print_function, division, absolute_import, with_statement,
                        nested_scopes, generators)

from urllib2 import urlopen
import os

script_dir = os.path.abspath(os.path.dirname(__file__))
join = os.path.join

from skimage.transform import pyramid_reduce
from scipy.ndimage import imread
import astropy.units as u

#from syotools.models import Telescope
from syotools.interface import SYOTool


#pre_url = "file://" + script_dir + "/static/"
pre_url = join(script_dir, "static")

"""prefetch_images = {"Galaxy (z=2)": pre_url+"HDST_source_z2.jpg",
                   "Deep Field": pre_url+"hdst16m_rgb_nosmoothing_3mas.jpg",
                   "Star Forming Region":  pre_url+"pretty.png",
                   "Perseus A": pre_url+"ngc1275_large.png",
                   "Pluto": pre_url+"pluto_16m.jpg"}"""
prefetch_images = {"Galaxy (z=2)": join(pre_url,"HDST_source_z2.jpg"),
                   "Deep Field": join(pre_url,"hdst16m_rgb_nosmoothing_3mas.jpg"),
                   "Star Forming Region":  join(pre_url,"pretty.png"),
                   "Perseus A": join(pre_url,"ngc1275_large.png"),
                   "Pluto": join(pre_url,"pluto_16m.jpg")}

interface_format = """
Figure:
    tools: "pan,resize,save,box_zoom,wheel_zoom,reset"
    toolbar_location: "above"
    background_fill_color: "white"
"""
                                   
class ImageComparison(SYOTool):
    
    def tool_preinit(self):
        """
        Pre-initialize any required attributes for the interface.
        """
        #initialize various attributes
        #self.telescope = Telescope()
        self.aperture = 12.0 * u.m
        self.hst_aperture = 2.4 * u.m
        self.current_image = "Galaxy (z=2)"
        self.image_options = prefetch_images.keys()
        
        #Formatting & interface stuff:
        self.format_string = interface_format
        self.interface_file = join(script_dir, "interface.yaml")
        
    def tool_postinit(self):
        """
        Set the initial figures.
        """
        self.from_default("", "", "Galaxy (z=2)")

    def load_url(self):
        """
        Use urlopen and imread to load an image from a URL.
        """
        
        f = urlopen(self.current_image)
        
        self.obs_image = imread(f)
        self.controller("", "", "")
        
    def from_url(self):
        """
        Load an image via a URL from the TextInput.
        """
        self.current_image = self.refs["url_input"].value
        self.load_url()
    
    def from_default(self, attr, old, new):
        """
        Load one of the default images.
        """
        self.current_image = prefetch_images[self.current_image]
        self.obs_image = imread(self.current_image)
        self.controller("", "", "")
        #self.load_url()
    
    def from_upload(self, attr, old, new):
        """
        Load an image via a file upload.
        """
        self.current_image = self.refs["image_upload"]
        self.load_url()
    
    def controller(self, attr, old, new):
        """
        Controller function for the tool, used as a generic(/global) callback.
        """
        self.aperture = self.refs["ap_slider"].value * u.m
        #self.telescope.aperture = self.aperture
        self.hst_image = self.prepare()
        
        #Set images in figures
        self.refs["obs_figure"].image(image=[self.obs_image], x=[0], y=[0],
                                    dw=10, dh=10)
        self.refs["hst_figure"].image(image=[self.hst_image], x=[0], y=[0],
                                    dw=10, dh=10)
        
    def prepare(self):
        """
        Create the downsampled HST image.
        """
        
        scale = (self.aperture / self.hst_aperture).decompose().value
        return pyramid_reduce(self.obs_image, downscale=scale)
    

"""import pdb, traceback, sys

try:
    ImageComparison()
except:
    typ, value, tb = sys.exc_info()
    traceback.print_exc()
    pdb.post_mortem(tb)"""
ImageComparison()
