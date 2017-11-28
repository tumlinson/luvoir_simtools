#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 30 12:31:11 2017

@author: gkanarek
"""

from __future__ import (print_function, division, absolute_import, with_statement,
                        nested_scopes, generators)

import numpy as np
import astropy.units as u

from syotools.models.base import PersistentModel
from syotools.defaults import default_exposure
from syotools.utils import pre_encode, pre_decode
from syotools.spectra import SpectralLibrary
from syotools.spectra.utils import renorm_sed

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

class Exposure(PersistentModel):
    """
    The base exposure class, which provides parameter storage for 
    optimization, and all exposure-specific calculations.
    
    This class encompasses both imaging and spectral exposures -- we will
    assume that all calculations are performed with access to the full SED 
    (which is simply interpolated to the correct wavebands for imaging).
    
    The SNR, exptime, and limiting magnitude can each be calculated from the
    other two. To trigger such calculations when parameters are updated, we
    will need to create property setters.
    
    Attributes:
        telescope    - the Telescope model instance associated with this exposure
        camera       - the Camera model instance associated with this exposure
        spectrograph - the Spectrograph model instance (if applicable) associated
                       with this exposure
    
        exp_id       - a unique exposure ID, used for save/load purposes (string)
                        NOTE: THIS HAS NO DEFAULT, A NEW EXP_ID IS CREATED
                        WHENEVER A NEW CALCULATION IS SAVED.
        sed_flux     - the spectral energy distribution of the target (float array)
        sed_wav      - the wavelengths associated with the SED flux (float array)
        sed_id       - for default (pysynphot) spectra, the id (i.e. the key 
                       into the default spectra dictionary), otherwise "user" (string)
        n_exp        - the desired number of exposures (integer)
        exptime      - the desired exposure time (float array)
        snr          - the desired S/N ratio (float array)
        magnitude    - either the input source magnitude, in which case this is
                       equal to the SED interpolated to the desired wavelengths,
                       or the limiting magnitude of the exposure (float array)
        unknown      - a flag to indicate which variable should be calculated
                       ('snr', 'exptime', or 'magnitude'). this should generally 
                       be set by the tool, and not be available to users. (string)
        
        _default_model - used by PersistentModel
    """
    
    _default_model = default_exposure
    
    telescope = None
    camera = None
    spectrograph = None
    
    exp_id = ''
    _sed = pre_encode(np.zeros(1, dtype=float) * u.ABmag) #default is set via sed_id
    _sed_id = ''
    n_exp = 0
    _exptime = pre_encode(np.zeros(1, dtype=float) * u.s)
    _snr = pre_encode(np.zeros(1, dtype=float) * u.dimensionless_unscaled)
    _magnitude = pre_encode(np.zeros(1, dtype=float) * u.ABmag)
    _unknown = '' #one of 'snr', 'magnitude', 'exptime'
    
    verbose = False #set this for debugging purposes only
    _disable = False #set this to disable recalculating (when updating several attributes at the same time)
    
    def disable(self):
        self._disable = True
    
    def enable(self):
        self._disable = False
        self.calculate()
    
    #Property wrappers for the three possible uknowns, so that we can auto-
    #calculate whenever they're set, and to prevent overwriting previous
    #calculations by accident.
    
    @property
    def unknown(self):
        return self._unknown
    
    @unknown.setter
    def unknown(self, new_unknown):
        self._unknown = new_unknown
        self.calculate()
    
    def _ensure_array(self, quant):
        """
        Ensure that the given Quantity is an array, propagating if necessary.
        """
        q = pre_encode(quant)
        if len(q) < 2:
            import pdb; pdb.set_trace()
        val = q[1]['value']
        if not isinstance(val, list):
            nb = self.recover('camera.n_bands')
            q[1]['value'] = np.full(nb, val).tolist()
        
        return q
    
    @property
    def exptime(self):
        return self._exptime
    
    @exptime.setter
    def exptime(self, new_exptime):
        if self.unknown == "exptime":
            return
        self._exptime = self._ensure_array(new_exptime)
        self.calculate()
    
    @property
    def snr(self):
        return self._snr
    
    @snr.setter
    def snr(self, new_snr):
        if self.unknown == "snr":
            return
        self._snr = self._ensure_array(new_snr)
        self.calculate()
    
    @property
    def sed(self):
        return self._sed
    
    @sed.setter
    def sed(self, new_sed):
        self._sed = pre_encode(new_sed)
        self.calculate()
        
    @property
    def sed_id(self):
        return self._sed_id
    
    @sed_id.setter
    def sed_id(self, new_sed_id):
        self._sed_id = new_sed_id
        self._sed = pre_encode(SpectralLibrary.get(new_sed_id, SpectralLibrary.fab))
        self.calculate()
        
    def renorm_sed(self, new_mag):
        sed = self.recover('sed')
        self.sed = renorm_sed(sed, pre_decode(new_mag))
    
    @property
    def interpolated_sed(self):
        """
        The exposure's SED interpolated at the camera bandpasses.
        """
        sed = self.recover('sed')
        return pre_encode(self.camera.interpolate_at_bands(sed))
    
    @property
    def magnitude(self):
        if self.unknown == "magnitude":
            return self._magnitude
        #If magnitude is not unknown, it should be interpolated from the SED
        #at the camera bandpasses. 
        return self.interpolated_sed
    
    @magnitude.setter
    def magnitude(self, new_magnitude):
        if self.unknown == "magnitude":
            return
        self._magnitude = self._ensure_array(new_magnitude)
        self.calculate()
        
    def calculate(self):
        """
        Wrapper to calculate the exposure time, SNR, or limiting magnitude, 
        based on the other two. The "unknown" attribute controls which of these
        parameters is calculated.
        """
        if self._disable:
            return False
        if self.camera is None or self.telescope is None:
            return False
        status = {'magnitude': self._update_magnitude,
                  'exptime': self._update_exptime,
                  'snr': self._update_snr}[self.unknown]()
        return status
    
    #Calculation methods
    
    @property
    def _fstar(self):
        """
        Calculate the stellar flux as per Eq 2 in the SNR equation paper.
        """
        mag = self.recover('magnitude')
        (f0, c_ap, D, dlam) = self.recover('camera.ab_zeropoint', 
                                           'camera.ap_corr', 
                                           'telescope.aperture', 
                                           'camera.derived_bandpass')
        
        m = 10.**(-0.4*(mag.value))
        D = D.to(u.cm)
        
        fstar = f0 * c_ap * np.pi / 4. * D**2 * dlam * m

        return fstar
    
    
    def _update_exptime(self):
        """
        Calculate the exposure time to achieve the desired S/N for the 
        given SED.
        """
        
        self.camera._print_initcon(self.verbose)
        
        #We no longer need to check the inputs, since they are now tracked
        #attributes instead.
               
        #Convert JsonUnits to Quantities for calculations
        (_snr, _nexp) = self.recover('snr', 'n_exp')
        (_total_qe, _detector_rn, _dark_current) = self.recover('camera.total_qe', 
                'camera.detector_rn', 'camera.dark_current')
        
        snr2 = -(_snr**2)
        fstar = self._fstar
        fsky = self.camera._fsky(verbose=self.verbose)
        Npix = self.camera._sn_box(self.verbose)
        thermal = pre_decode(self.camera.c_thermal(verbose=self.verbose))
        
        a = (_total_qe * fstar)**2
        b = snr2 * (_total_qe * (fstar + fsky) + thermal + _dark_current * Npix)
        c = snr2 * _detector_rn**2 * Npix * _nexp
        
        texp = ((-b + np.sqrt(b**2 - 4*a*c)) / (2*a)).to(u.s)
        
        #serialize with JsonUnit for transportation
        self._exptime = pre_encode(texp)
        
        return True #completed successfully
        
    def _update_magnitude(self):
        """
        Calculate the limiting magnitude given the desired S/N and exposure
        time.
        """
        
        self.camera._print_initcon(self.verbose)
        
        #We no longer need to check the inputs, since they are now tracked
        #attributes instead.
            
        #Grab values for calculation
        (_snr, _exptime, _nexp) = self.recover('snr', 'exptime', 'n_exp')
        (f0, c_ap, D, dlam) = self.recover('camera.ab_zeropoint', 
                                           'camera.ap_corr', 
                                           'telescope.aperture', 
                                           'camera.derived_bandpass')
        (QE, RN, DC) = self.recover('camera.total_qe', 
                                    'camera.detector_rn', 
                                    'camera.dark_current')
        
        exptime = _exptime.to(u.s)
        D = D.to(u.cm)
        fsky = self.camera._fsky(verbose=self.verbose)
        Npix = self.camera._sn_box(self.verbose)
        c_t = pre_decode(self.camera.c_thermal(verbose=self.verbose))
        
        snr2 = -(_snr ** 2)
        a0 = (QE * exptime)**2
        b0 = snr2 * QE * exptime
        c0 = snr2 * ((QE * fsky + c_t + Npix * DC) * exptime + (RN**2 * Npix * _nexp))
        k = (-b0 + np.sqrt(b0**2 - 4. * a0 * c0)) / (2. * a0)
        
        flux = (4. * k) / (f0 * c_ap * np.pi * D**2 * dlam)
        
        self._magnitude = pre_encode(-2.5 * np.log10(flux.value) * u.mag('AB'))
        
        return True #completed successfully
    
    def _update_snr(self):
        """
        Calculate the SNR for the given exposure time and SED.
        """
        
        self.camera._print_initcon(self.verbose)
        
        #We no longer need to check the inputs, since they are now tracked
        #attributes instead.
            
        #Convert JsonUnits to Quantities for calculations
        (_exptime, _nexp, n_bands) = self.recover('_exptime', 'n_exp',
                                                  'camera.n_bands')
        (_total_qe, _detector_rn, _dark_current) = self.recover('camera.total_qe',
                             'camera.detector_rn', 'camera.dark_current')
        
        #calculate everything
        number_of_exposures = np.full(n_bands, _nexp)
        desired_exp_time = (np.full(n_bands, _exptime.value) * _exptime.unit).to(u.second)
        time_per_exposure = desired_exp_time / number_of_exposures
        
        fstar = self._fstar
        signal_counts = _total_qe * fstar * desired_exp_time
        
        fsky = self.camera._fsky(verbose=self.verbose)
        sky_counts = _total_qe * fsky * desired_exp_time
        
        shot_noise_in_signal = np.sqrt(signal_counts)
        shot_noise_in_sky = np.sqrt(sky_counts)
        
        sn_box = self.camera._sn_box(self.verbose)
        
        read_noise = _detector_rn**2 * sn_box * number_of_exposures
        dark_noise = sn_box * _dark_current * desired_exp_time

        thermal = pre_decode(self.camera.c_thermal(verbose=self.verbose))
        
        thermal_counts = desired_exp_time * thermal
        
        snr = signal_counts / np.sqrt(signal_counts + sky_counts + read_noise
                                      + dark_noise + thermal_counts)
        
        if self.verbose:
            print('# of exposures: {}'.format(_nexp))
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
            print('Max SNR: {} in {} band'.format(snr.max(), self.camera.bandnames[snr.argmax()]))
        
        #serialize with JsonUnit for transportation
        self._snr = pre_encode(snr)
        
        return True #completed successfully