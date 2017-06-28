#!/usr/bin/env python
"""
Created on Fri Oct 14 21:31:18 2016

@author: gkanarek, tumlinson
"""

from __future__ import (print_function, division, absolute_import, with_statement,
                        nested_scopes, generators)

import numpy as np
import astropy.constants as const
import astropy.units as u

from syotools.models.base import PersistentModel
from syotools.defaults import default_camera
from syotools.utils import pre_encode, pre_decode

def nice_print(arr):
    """
    Utility to make the verbose output more readable.
    """
    
    arr = pre_decode(arr) #in case it's a JsonUnit serialization

    if isinstance(arr, u.Quantity):
        l = ['{:.2f}'.format(i) for i in arr.value]
    else:
        l = ['{:.2f}'.format(i) for i in arr]
    return ', '.join(l)

class Camera(PersistentModel): 
    """
    The basic camera class, which provides parameter storage for 
    optimization.
    
    Attributes: #adapted from the original in Telescope.py
        telescope    - the Telescope object associated with the camera
    
        name         - name of the camera (string)
        n_bands      - number of wavelength bands (int)
        n_channels   - number of channels (int)
        pivotwave    - central wavelengths for bands, in nanometers (float array)
        bandnames    - names of bands (string list)
        channels     - grouping of bands into channels [UV, Optical, IR], 
                       and indicating the reference band for pixel size (list of tuples)
        ab_zeropoint - flux zero-point for each band in photons/s/cm2/nm (float array)
        total_qe     - total quantum efficiency in each band (float array)
        ap_corr      - magnitude correction factor for aperture size (float array)
        bandpass_r   - resolution in each bandpass (float array)
        dark_current - dark current values in each band (float array)
        detector_rn  - read noise for the detector in each band (float array)
        
        _default_model - used by PersistentModel
        
    The following are attributes I haven't included, and the justification:
        R_effective - this doesn't seem to be used anywhere
    """
    
    _default_model = default_camera
    
    telescope = None
    
    name = ''
    pivotwave = pre_encode(np.zeros(1, dtype=float) * u.nm)
    bandnames = ['']
    channels = [([],0)]
    ab_zeropoint = pre_encode(np.zeros(1, dtype=float) * (u.photon / u.s / u.cm**2 / u.nm))
    total_qe = pre_encode(np.zeros(1, dtype=float) * u.dimensionless_unscaled)
    ap_corr = pre_encode(np.zeros(1, dtype=float) * u.dimensionless_unscaled)
    bandpass_r = pre_encode(np.zeros(1, dtype=float) * u.dimensionless_unscaled)
    dark_current = pre_encode(np.zeros(1, dtype=float) * (u.electron / u.s / u.pixel))
    detector_rn = pre_encode(np.zeros(1, dtype=float) * (u.electron / u.pixel))
    
    @property
    def pixel_size(self):
        """
        Compute the pixel size as a function of pivot wavelength.
        
        Use the reference band for each channel as the fiducial: U-band for UV 
        and optical, J-band for IR.
        """
        
        pixsize = np.zeros(self.n_bands, dtype=float)
        
        #Convert from JsonUnit to Quantity for calculation purposes.
        pivotwave, aperture = self.recover('pivotwave', 'telescope.aperture')
        
        for bands, ref in self.channels:
            pxs = (0.61 * u.rad * pivotwave[ref] / aperture).to(u.arcsec)
            pixsize[bands] = pxs
        
        #serialize with JsonUnit for transportation purposes.
        return pre_encode(pixsize * u.arcsec / u.pix)
    
    @property
    def n_bands(self):
        return len(self.bandnames)
    
    @property
    def n_channels(self):
        return len(self.channels)
    
    @property
    def derived_bandpass(self):
        """
        Calculate the bandpasses.
        """
        
        #Convert to Quantity for calculations.
        pivotwave, bandpass_r = self.recover('pivotwave','bandpass_r')
        
        #serialize with JsonUnit for transportation.
        return pre_encode(pivotwave / bandpass_r)
    
    @property
    def fwhm_psf(self):
        """
        Calculate the FWHM of the camera's PSF.
        """
        #Convert to Quantity for calculations.
        pivotwave, aperture = self.recover('pivotwave','telescope.aperture')
        
        fwhm = (1.22 * u.rad * pivotwave / aperture).to(u.arcsec)
        #serialize with JsonUnit for transportation.
        return pre_encode(fwhm)
    
    def signal_to_noise(self, exptime, n_exp, magnitude, verbose=True):
        """
        Calculate the SNR for the given exposure time and SED.
        
        exptime   - desired exposure time. Must be a Quantity.
        n_exp     - desired number of exposures.
        magnitude - AB magnitudes for the source. This can be a single value, in
                    which case it will be used for all bands, or a float array
                    of 1 mag per band.
        """
        
        if verbose: #These are our initial conditions
            print('Telescope diffraction limit: {}'.format(self.telescope.diff_limit_arcsec))
            print('Telescope aperture: {}'.format(self.telescope.aperture))
            print('Telescope temperature: {}'.format(self.telescope.temperature))
            print('Pivot waves: {}'.format(nice_print(self.pivotwave)))
            print('Pixel sizes: {}'.format(nice_print(self.pixel_size)))
            print('AB mag zero points: {}'.format(nice_print(self.ab_zeropoint)))
            print('Quantum efficiency: {}'.format(nice_print(self.total_qe)))
            print('Aperture correction: {}'.format(nice_print(self.ap_corr)))
            print('Bandpass resolution: {}'.format(nice_print(self.bandpass_r)))
            print('Derived_bandpass: {}'.format(nice_print(self.derived_bandpass)))
            print('Detector read noise: {}'.format(nice_print(self.detector_rn)))
            print('Dark rate: {}'.format(nice_print(self.dark_current)))
        
        #Check inputs
        if not isinstance(exptime, u.Quantity):
            raise TypeError('Exposure time must be a Quantity')
            #We don't need to enforce the particular time unit, because astropy
            #unit conversions handle this for us.
        if not isinstance(magnitude, u.Quantity) or magnitude.unit != u.mag('AB'):
            raise TypeError('Magnitude must be a Quantity with units of AB mag')
        
        #If magnitude is an array, verify array length; otherwise, convert to
        #array
        if isinstance(magnitude, np.ndarray):
            if magnitude.size != self.n_bands:
                raise ValueError('Magnitude array must have {} elements'.format(self.n_bands))
        else:
            magnitude = np.full(self.n_bands, magnitude.value) * magnitude.unit
        
        #Should this actually be hardcoded in this function? 
        #Or can we store/calculate it somewhere? Maybe in defaults?
        sky_brightness = np.array([23.807, 25.517, 22.627, 22.307, 21.917, 
                                   22.257, 21.757, 21.567, 22.417, 22.537]) * u.mag('AB')
        
        if verbose:
            print('Source magnitudes: {}'.format(nice_print(magnitude)))
            print('Sky brightness: {}'.format(nice_print(sky_brightness)))
        
        #Convert JsonUnits to Quantities for calculations
        (_fwhm_psf, _diff_limit_arcsec, _pixel_size, _total_qe,
         _ab_zeropoint, _aperture, _derived_bandpass, _ap_corr,
         _detector_rn, _dark_current) = self.recover('fwhm_psf', 
                             'telescope.diff_limit_arcsec', 'pixel_size',
                             'total_qe', 'ab_zeropoint', 'telescope.aperture',
                             'derived_bandpass', 'ap_corr', 'detector_rn',
                             'dark_current')
        
        #calculate everything
        fwhm_psf = np.maximum(_fwhm_psf, _diff_limit_arcsec)
        sn_box = np.round(3. * fwhm_psf / _pixel_size)
        number_of_exposures = np.full(self.n_bands, n_exp)
        desired_exp_time = (np.full(self.n_bands, exptime.value) * exptime.unit).to(u.second)
        time_per_exposure = desired_exp_time / number_of_exposures
        
        flux_convert = lambda mag: 10.**(-0.4*(mag.value))
        
        base_counts = (_total_qe * desired_exp_time * _ab_zeropoint * np.pi /
                       4. * (_aperture.to(u.cm))**2 * _derived_bandpass)
        signal_counts = base_counts * _ap_corr * flux_convert(magnitude)
        sky_counts = (base_counts * flux_convert(sky_brightness) / u.arcsec**2 * 
                      (_pixel_size * sn_box)**2)
                      
        shot_noise_in_signal = np.sqrt(signal_counts)
        shot_noise_in_sky = np.sqrt(sky_counts)
        
        read_noise = _detector_rn * sn_box * np.sqrt(number_of_exposures) / u.electron**0.5
        dark_noise = sn_box * np.sqrt(_dark_current * desired_exp_time) / u.pix**0.5
        
        thermal = pre_decode(self.c_thermal(sn_box**2, verbose=verbose))
        
        thermal_counts = desired_exp_time * thermal
    
        snr = signal_counts / np.sqrt(signal_counts + sky_counts + read_noise**2 
                                      + dark_noise**2 + thermal_counts)
        
        if verbose:
            print('PSF width: {}'.format(nice_print(fwhm_psf)))
            print('SN box width: {}'.format(nice_print(sn_box)))
            print('# of exposures: {}'.format(n_exp))
            print('Time per exposure: {}'.format(time_per_exposure[0]))
            print('Signal counts: {}'.format(nice_print(signal_counts)))
            print('Signal shot noise: {}'.format(nice_print(shot_noise_in_signal)))
            print('Sky counts: {}'.format(nice_print(sky_counts)))
            print('Sky shot noise: {}'.format(nice_print(shot_noise_in_sky)))
            print('Total read noise: {}'.format(nice_print(read_noise)))
            print('Dark current noise: {}'.format(nice_print(dark_noise)))
            print('Thermal counts: {}'.format(nice_print(thermal_counts)))
            print()
            print('SNR: {}'.format(snr))
            print('Max SNR: {} in {} band'.format(snr.max(), self.bandnames[snr.argmax()]))
            
        #serialize with JsonUnit for transportation
        return pre_encode(snr)
    
    def c_thermal(self, box, verbose=True):
        """
        Calculate the thermal emission counts for the telescope.
        """
        
        #Convert to Quantities for calculation.
        (bandpass, pivotwave, aperture, ota_emissivity, 
         total_qe, pixel_size) = self.recover('derived_bandpass', 'pivotwave', 
                'telescope.aperture',  'telescope.ota_emissivity', 'total_qe',
                'pixel_size')
        
        bandwidth = bandpass.to(u.cm)
    
        h = const.h.to(u.erg * u.s) # Planck's constant erg s 
        c = const.c.to(u.cm / u.s) # speed of light [cm / s] 
    
        energy_per_photon = h * c / pivotwave.to(u.cm) / u.ph
    
        D = aperture.to(u.cm) # telescope diameter in cm 
    
        Omega = (2.3504e-11 * pixel_size**2 * box).to(u.sr)
        
        planck = pre_decode(self.planck)
        qepephot = total_qe * planck / energy_per_photon
        
        if verbose:
            print('Planck spectrum: {}'.format(nice_print(planck)))
            print('QE * Planck / E_phot: {}'.format(nice_print(qepephot)))
            print('E_phot: {}'.format(nice_print(energy_per_photon)))
            print('Omega: {}'.format(nice_print(Omega)))
    
        thermal = (ota_emissivity * planck / energy_per_photon * 
    			(np.pi / 4. * D**2) * total_qe * Omega * bandwidth )
        
        #serialize with JsonUnit for transportation
        return pre_encode(thermal) 
    
    @property
    def planck(self):
        """
        Planck spectrum for the various wave bands.
        """
        #Convert to Quantities for calculation
        pivotwave, temperature = self.recover('pivotwave', 'telescope.temperature')
        
        wave = pivotwave.to('cm')
        temp = temperature.to('K')
        h = const.h.to(u.erg * u.s) # Planck's constant erg s 
        c = const.c.to(u.cm / u.s) # speed of light [cm / s] 
        k = const.k_B.to(u.erg / u.K) # Boltzmann's constant [erg deg K^-1] 
        x = 2. * h * c**2 / wave**5 
        exponent = (h * c / (wave * k * temp)) 
    
        result = (x / (np.exp(exponent)-1.)).to(u.erg / u.s / u.cm**3) / u.sr
        
        #serialize with JsonUnit for transportation
        return pre_encode(result)
            