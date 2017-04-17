#!/usr/bin/env python
"""
Created on Tue Oct 18 15:23:49 2016

@author: gkanarek
"""

from __future__ import (print_function, division, absolute_import, with_statement,
                        nested_scopes, generators)

import astropy.units as units
import numpy as np

import syotools.coronagraph as cg
from syotools.models.base import PersistentModel
from syotools.defaults import default_coronagraph

class Coronagraph(PersistentModel):
    """
    The basic coronagraph class, which provides parameter storage for 
    optimization.
    
    Unlike other models, most of the calculations for this will be handled by
    the coronagraph package. This is mostly for parameter storage and initial
    conditions prep.
    
    Attributes: #adapted from the original in coron_model.py
        engine       - coronograph module instance
        count_rates  - output dict from coronograph.count_rates
    
        int_time     - Integration time for Bokeh slider, in hours (float)
        phase_angle  - planetary phase angle at quadrature, in degrees (float)
        phase_func   - planetary phase function at quadrature (already included in SMART run) (float)
        r_planet     - planetary radius in Earth radii for Bokeh slider (float)
        semimajor    - semi-major orbital axis in AU for Bokeh slider (float)
        t_eff        - Stellar effective temperature in K for Sun-like star (float)
        r_star       - Stellar radius in solar radii (float)
        d_system     - distance to planetary system in pc for Bokeh slider (float)
        n_exoz       - number of exo-zodis for Bokeh slider (float)
        wave         - hi-resolution wavelength array for Earth spectrum in microns (float array)
        radiance     - hi-resolution radiance array for Earth spectrum in W/m**2/um/sr (float array)
        sol_flux     - hi-resolution solar flux array for Earth spectrim in W/m**2/um (float array)
        
        _default_model - used by PersistentModel
    """
    
    _default_model = default_coronagraph
    
    engine = cg
    count_rates = {}
    
    int_time = 0. * units.hr
    phase_angle = 0. * units.deg
    phase_func = 1.
    r_planet = 1. * units.R_earth
    semimajor = 1. * units.au
    t_eff = 0. * units.K
    r_star = 1. * units.R_sun
    d_system = 0. * units.pc
    n_exoz = 1.
    wave = np.zeros(0, dtype=float) * units.um
    radiance = np.zeros(0, dtype=float) * (units.W / units.m**2 / units.um / units.sr)
    sol_flux = np.zeros(0, dtype=float) * (units.W / units.m**2 / units.um)
    
    
    def __init__(self, *arg, **kw):
        super().__init__(*arg, **kw)
        self._calc_count_rates()
    
    @property
    def albedo(self):
        """
        Planetary albedo spectrum.
        """
        return np.pi * units.sr * (np.pi * self.radiance / self.sol_flux).decompose()
    
    def _calc_count_rates(self):
        """
        Compute the coronagraphic model using the coronagraph package.
        """
        al = self.albedo.value
        wv = self.wave.to(units.um).value
        sf = self.sol_flux.to(units.W / units.m**2 / units.um).value
        pa = self.phase_angle.to(units.deg).value
        pf = self.phase_func.value
        rp = self.r_planet.to(units.R_earth).value
        te = self.t_eff.to(units.K).value
        rs = self.r_star.to(units.R_sun).value
        sm = self.semimajor.to(units.au).value
        ds = self.d_system.to(units.pc).value
        ez = self.n_exoz.value
        cr = cg.count_rates(al, wv, sf, pa, pf, rp, te, rs, sm, ds, ez)
        self._count_rates = dict(*zip(['wavelength','wave_bin','albedo',
                                       'quant_eff','flux_ratio','planet_cr',
                                       'speckle_cr','zodi_cr','exoz_cr',
                                       'dark_cr','read_cr','thermal_cr',
                                       'dtsnr'], cr))
    
    @property
    def background_cr(self):
        """
        Background photon count rates.
        """
        return sum([self._count_rates[x] for x in ['zodi_cr', 'exoz_cr', 
                                                   'speckle_cr', 'dark_cr',
                                                   'read_cr', 'thermal_cr']])
    
    @property
    def dts(self):
        """
        Integration time in seconds
        """
        return self.int_time.to(units.s).value
    
    @property
    def snr(self):
        """
        Calculate the SNR based on count rates.
        """
        pcr = self._count_rates['planet_cr']
        bcr = self.background_cr
        dts = self.dts
        return pcr * dts / np.sqrt((pcr + 2*bcr) * dts)
    
    @property
    def sigma(self):
        """
        Calculate the 1-sigma errors.
        """
        return self._count_rates['flux_ratio'] / self.snr

    @property
    def spectrum(self):
        """
        Create a spectrum by adding random noise to the flux ratio.
        """
        c_ratio = self._count_rates['flux_ratio']
        return c_ratio + np.random.randn(len(c_ratio)) * self.sigma

    @property
    def planet(self):
        """
        Generate the planet data dictionary for Bokeh.
        """
        spec = self.spectrum
        sig = self.sigma
        return {'lam':self._count_rates['wavelength'],
                'cratio': self._count_rates['flux_ratio'] * 1.e9,
                'spec': spec * 1.e9,
                'downerr': (spec - sig) * 1.e9,
                'uperr': (spec + sig) * 1.e9}
