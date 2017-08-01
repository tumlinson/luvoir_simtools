# define a telescope class 
from __future__ import print_function
import numpy as np 
import os 
from astropy.io import ascii 

class Telescope: 

    def __init__(self, aperture,temperature,diff_limit_wavelength):
        self.name = 'LUVOIR' 
        self.aperture = 10. # aperture in meters 
        self.temperature = 270. # temperature in Kelvin 
        self.ota_emissivity = 0.09 # emissivity factor for a TMA 
        self.diff_limit_wavelength = 500. # in nanometers 
        diff_limit_in_arcsec = 1.22*(self.diff_limit_wavelength*0.000000001)*206264.8062/self.aperture

class Camera(): 

    def __init__(self): 

        self.name = 'HDI' 
        self.pivotwave = np.array([155., 228., 360., 440., 550., 640., 790., 1260., 1600., 2220.])
        self.bandnames = ['FUV', 'NUV', 'U','B','V','R','I', 'J', 'H', 'K'] 
        self.R_effective = np.array([5., 5., 5., 5., 5., 5., 5., 5., 5., 5.])

        self.ab_zeropoint = np.array([35548., 24166., 15305., 12523., 10018., 8609., 6975., 4373., 3444., 2482.])

        self.total_qe = np.array([0.1, 0.1, 0.15, 0.45, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6])
        self.aperture_correction = np.array([1., 1., 1., 1., 1., 1., 1., 1., 1., 1.])
        self.bandpass_r = np.array([5., 5., 5., 5., 5., 5., 5., 5., 5., 5.])
        self.derived_bandpass = self.pivotwave / self.bandpass_r
        self.dark_current = np.array([0.0005, 0.0005, 0.001, 0.001, 0.001, 0.001, 0.001, 0.002, 0.002, 0.002])
        self.detector_read_noise = np.array([3., 3., 3., 3., 3., 3., 3., 4., 4., 4.])

        self.pixel_size = np.array([0.016, 0.016, 0.016, 0.016, 0.016, 0.016, 0.016, 0.04, 0.04, 0.04])

        
    def set_pixel_sizes(self, telescope): 

        self.pixel_size = 1.22*(self.pivotwave*0.000000001)*206264.8062/telescope.aperture / 2. 
        # this enforces the rule that the pixel sizes are set at the shortest wavelength in each channel 
        self.pixel_size[0:2] = 1.22*(self.pivotwave[2]*0.000000001)*206264.8062/telescope.aperture / 2.   # UV set at U 
        self.pixel_size[2:-3] = 1.22*(self.pivotwave[2]*0.000000001)*206264.8062/telescope.aperture / 2.   # Opt set at U 
        self.pixel_size[-3:] = 1.22*(self.pivotwave[7]*0.000000001)*206264.8062/telescope.aperture / 2.   # NIR set at J 

class Spectrograph(): 

    def __init__(self): 

        cwd = os.getenv('LUVOIR_SIMTOOLS_DIR')

        g120 = ascii.read(cwd+'/data/G120M_ETC.dat') 
        self.name = 'LUMOS' 
        self.wave = g120["Wavelength"] 
        self.aeff = g120['A_Eff']
        self.bef = g120["BEF"] * g120["XDisp_Width"] * (1. / (g120["Wavelength"][100] - g120["Wavelength"][99]) ) 
        self.delta_lambda = self.wave / 30000. 
        self.lumos_table = g120 
        self.lambda_range = np.array([925., 1475.]) 
        self.mode_name = 'G120M' 
        self.R = 30400. 

    def set_mode(self, mode_name): 

        self.mode_names = mode_name 
        cwd = os.getenv('LUVOIR_SIMTOOLS_DIR')

        if 'G120M' in mode_name:
            print('Setting the spectrograph to mode: ', mode_name) 
            g120 = ascii.read(cwd+'/data/G120M_ETC.dat') 
            self.bef = g120["BEF"] * g120["XDisp_Width"] * (1. / (g120["Wavelength"][100] - g120["Wavelength"][99]) ) # last term is 1 / wave interval 
            self.wave = g120["Wavelength"] 
            self.delta_lambda = self.wave / 30400. 
            self.lambda_range = np.array([900., 2500.]) 
            self.mode_name = 'G120M' 
            self.R = 30400. 
            self.aeff = g120["A_Eff"] 

        if 'G150M' in mode_name: 
            print('Setting the spectrograph to mode: ', mode_name) 
            g150 = ascii.read(cwd+'/data/G150M_ETC.dat') 
            self.wave = g150["Wavelength"] 
            self.bef = g150["BEF"] * g150["XDisp_Width"] * (1. / (g150["Wavelength"][100] - g150["Wavelength"][99]) ) # last term is 1 / wave interval 
            self.delta_lambda = self.wave / 37800. 
            self.lambda_range = np.array([1234., 1765.]) 
            self.mode_name = 'G150M' 
            self.R = 37800. 
            self.aeff = g150["A_Eff"] 
          
        if 'G180M' in mode_name: 
            print('Setting the spectrograph to mode: ', mode_name) 
            g180 = ascii.read(cwd+'/data/G180M_ETC.dat') 
            self.wave = g180["Wavelength"] 
            self.bef = g180["BEF"] * g180["XDisp_Width"] * (1. / (g180["Wavelength"][100] - g180["Wavelength"][99]) ) # last term is 1 / wave interval 
            self.delta_lambda = self.wave / 40800. 
            self.lambda_range = np.array([1534., 2065.]) 
            self.mode_name = 'G180M' 
            self.R = 40800. 
            self.aeff = g180["A_Eff"] 
          
        if 'G155L' in mode_name: 
            print('Setting the spectrograph to mode: ', mode_name) 
            g155 = ascii.read(cwd+'/data/G155L_ETC.dat') 
            self.wave = g155["Wavelength"] 
            self.bef = g155["BEF"] * g155["XDisp_Width"] * (1. / (g155["Wavelength"][100] - g155["Wavelength"][99]) ) # last term is 1 / wave interval 
            self.delta_lambda = self.wave / 11600. 
            self.lambda_range = np.array([919., 2018.]) 
            self.mode_name = 'G155L' 
            self.R = 11600.
            self.aeff = g155["A_Eff"] 

        if 'G145LL' in mode_name: 
            print('Setting the spectrograph to mode: ', mode_name) 
            g145 = ascii.read(cwd+'/data/G145LL_ETC.dat') 
            self.wave = g145["Wavelength"] 
            self.bef = g145["BEF"] * g145["XDisp_Width"] * (1. / (g145["Wavelength"][100] - g145["Wavelength"][99]) ) # last term is 1 / wave interval 
            self.delta_lambda = self.wave / 500. 
            self.lambda_range = np.array([1000., 2000.]) 
            self.mode_name = 'G145LL' 
            self.R = 500. 
            self.aeff = g145["A_Eff"] 

        if 'G300M' in mode_name: 
            print('Setting the spectrograph to mode: ', mode_name) 
            g300 = ascii.read(cwd+'/data/G300M_ETC.dat') 
            self.wave = g300["Wavelength"] 
            self.bef = g300["BEF"] * g300["XDisp_Width"] * (1. / (g300["Wavelength"][100] - g300["Wavelength"][99]) ) # last term is 1 / wave interval 
            self.delta_lambda = self.wave / 28000. 
            self.lambda_range = np.array([2000., 4000.]) 
            self.mode_name = 'G300M' 
            self.R = 28000. 
            self.aeff = g300["A_Eff"] 


