#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Mon Jul  9 13:31:53 2018

@author: gkanarek
"""

from __future__ import (print_function, division, absolute_import, with_statement,
                        nested_scopes, generators)

import os
import StringIO
import base64
from six.moves.urllib.request import urlopen

script_dir = os.path.abspath(os.path.dirname(__file__))


import astropy.units as u
import numpy as np
from scipy.ndimage import imread
from skimage.transform import rescale as skrescale

from syotools import cdbs
from syotools.interface import SYOTool
from syotools.models import Telescope, Camera
from syotools.utils import pre_encode#, pre_decode

from numba import njit

#establish simtools dir
if 'LUVOIR_SIMTOOLS_DIR' not in os.environ:
    fdir = os.path.abspath(__file__)
    basedir = os.path.abspath(os.path.join(fdir, '..'))
    os.environ['LUVOIR_SIMTOOLS_DIR'] = basedir

interface_format = """
Figure:
    background_fill_color: "#1D1B4D"
Image:
    x: 0
    y: 0
    dw: 10
    dh: 10
Slider:
    callback_policy: 'mouseup'
"""

upload_js = """
function read_file(filename) {
    var reader = new FileReader();
    reader.onload = load_handler;
    reader.onerror = error_handler;
    // readAsDataURL represents the file's data as a base64 encoded string
    reader.readAsDataURL(filename);
}

function load_handler(event) {
    var b64string = event.target.result;
    file_source.data = {'file_contents' : [b64string], 'file_name':[input.files[0].name]};
    file_source.trigger("change");
}

function error_handler(evt) {
    if(evt.target.error.name == "NotReadableError") {
        alert("Can't read file!");
    }
}

var input = document.createElement('input');
input.setAttribute('type', 'file');
input.onchange = function(){
    if (window.FileReader) {
        read_file(input.files[0]);
    } else {
        alert('FileReader is not supported in this browser');
    }
}
input.click();
""" # from here: https://github.com/bokeh/bokeh/issues/6096#issuecomment-299002827

builtin_images = {'Gal': ("HDST_source_z2.jpg", "HST_source_z2.jpg"),
                  'Dee': ("hdst16m_rgb_nosmoothing_3mas.jpg",
                           "hdst2.4m_rgb_smoothing_60mas_dimmed.jpg"),
                  'Sta': ("pretty.png", "pretty_large.png"),
                  'Per': ("ngc1275_large.png", "ngc1275_small.png"),
                  'Plu': ("pluto_16m.jpg", "pluto_2.4m.jpg")}

HUBBLE_PIXEL = 0.004 * u.arcsec / u.pix

def hubble_fwhm(wave):
    aper = 2.4 * u.m
    fwhm = (1.03 * u.rad * wave / aper).to(u.arcsec)
    return fwhm / HUBBLE_PIXEL

@njit
def blur(image, fwhm):
    out = np.zeros_like(image)
    nx, ny = out.shape
    w = max(int(fwhm*2.5), 5)
    for i in range(nx):
        for j in range(ny):
            tweight = 0.
            value = 0.
            for kx in range(-w,w):
                ix = i + kx
                if ix < 0 or ix >= nx:
                    continue
                for ky in range(-w, w):
                    jy = j + ky
                    if jy < 0 or jy > ny:
                        continue
                    weight = np.exp(-(kx*kx + ky*ky) / (2. * fwhm**2))
                    tweight += weight
                    value += image[ix, jy] * weight
            out[i, j] = value / tweight
    return out

class ImageComparison(SYOTool):
    tool_prefix = "imc"
    
    verbose = True
    
    save_models = ["telescope", "camera"]
    save_params = {"aperture": ("telescope", "aperture")}
    
    save_dir = os.path.join(os.environ['LUVOIR_SIMTOOLS_DIR'],'saves')
    
    #must include this to set defaults before the interface is constructed
    tool_defaults = {'aperture': pre_encode(12.0 * u.m)}
    
    def tool_preinit(self):
        """
        Pre-initialize any required attributes for the interface.
        """
        #initialize engine objects
        self.telescope = Telescope(aperture=pre_encode(12.0 * u.m))
        self.camera = Camera() #we'll just use default camera
        self.telescope.add_camera(self.camera)
        
        #set interface variables
        self.image_options = ["Deep Field", "Pluto"]#["Galaxy (z=2)", "Deep Field", 
                             # "Star Forming Region", "Perseus A", 
                             # "Pluto"]
        
        #Formatting & interface stuff:
        self.format_string = interface_format
        self.interface_file = os.path.join(script_dir, "interface.yaml")
        
        self.upload_js = upload_js
    
    def tool_postinit(self):
        self.image_select(None, None, None)
    
    def image_select(self, attr, old, new):
        imsel = self.refs["image_select"].value
        self.default_images(imsel[:3])
    
    def aperture_update(self, attr, old, new):
        self.aperture = pre_encode(new["value"][0] * u.m)
        self.telescope.aperture = self.aperture
        self.set_images(self.luv_image)
    
    def set_images(self, l_im):
        luv_img = self.convert_rgba(l_im)
        self.refs["luvoir_source"].data.update(image=[luv_img])
        h_im = self.create_hst_image(l_im)
        hst_img = self.convert_rgba(h_im)
        self.refs["hubble_source"].data.update(image=[hst_img])
        
    @staticmethod
    def convert_rgba(img):
        if img.ndim > 2: # could also be img.dtype == np.uint8
            if img.shape[2] == 3: # alpha channel not included
                img = np.dstack([img, np.ones(img.shape[:2], np.uint8) * 255])
            img = np.squeeze(img.view(np.uint32))
        return img
    
    def read_image_from_url(self, url):
        f = urlopen(url)
        img = imread(f)
        f.close()
        return img
    
    def read_image_from_file(self, fname):
        img = imread(fname)
        return img
    
    def default_images(self, key):
        im1, im2 = builtin_images[key]
        f1 = os.path.join(script_dir, "..", "data", im1)
        #f2 = os.path.join(script_dir, "..", "data", im2)
        self.luv_image = self.read_image_from_file(f1)
        #hst_image = self.read_image_from_file(f2)
        self.set_images(self.luv_image)
        
    def upload(self, attr, old, new):
        file_source = self.refs["upload_source"]
        print('filename:', file_source.data['file_name'])
        raw_contents = file_source.data['file_contents'][0]
        # remove the prefix that JS adds  
        prefix, b64_contents = raw_contents.split(",", 1)
        file_contents = base64.b64decode(b64_contents)
        file_io = StringIO.StringIO(file_contents)
        self.luv_image = imread(file_io)
        self.set_images(self.luv_image)
    
    def create_hst_image(self, base_image):
        self.refs["ap_slider"].disabled = True
        print("Aperture: {}".format(self.telescope.recover("aperture")))
        ang_fwhm, pixscale, wave = self.camera.recover("fwhm_psf", 
                                                       "pixel_size", 
                                                       "pivotwave")
        #assume V band
        ang_fwhm = ang_fwhm[4]
        pixscale = pixscale[4]
        wave = wave[4]
        
        lfwhm = (ang_fwhm / pixscale).value
        hfwhm = hubble_fwhm(wave).value
        fwhm = hfwhm * lfwhm / np.sqrt(hfwhm**2 - lfwhm**2)

        resize_factor = (pixscale / HUBBLE_PIXEL).value
        
        if self.verbose:
            print("Angular fwhm: {}".format(ang_fwhm))
            print("Pixel scale: {}".format(pixscale))
            print("LUVOIR FWHM: {} px".format(lfwhm))
            print("HST FWHM: {} px".format(hfwhm))
            print("Final FWHM: {}".format(fwhm))
            print("Resize pixel scale: {}".format(resize_factor))
        
        if base_image.ndim > 2:
            n_channel = base_image.shape[2]
            out_image = np.zeros_like(base_image)
            for c in range(n_channel):
                out_image[:, :, c] = blur(base_image[:, :, c], fwhm)
            out_image = skrescale(out_image, resize_factor, anti_aliasing=False, 
                                  multichannel=True, preserve_range=True)
        else:
            out_image = blur(base_image, fwhm)
            out_image = skrescale(out_image, resize_factor, anti_aliasing=False,
                                  multichannel=False, preserve_range=True)
        
        if self.verbose:
            print("done")
        self.refs["ap_slider"].disabled = False
        return out_image.astype(np.uint8)
    
ImageComparison()