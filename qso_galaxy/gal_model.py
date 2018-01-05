# coding: utf-8
import matplotlib.pyplot as plt
import numpy as np
from astropy.table import QTable
import astropy.units as u
from astropy.coordinates import SkyCoord # AstroPy treatment of coordinates
from astroquery.simbad import Simbad # SIMBAD query functionality 
import os 

#this routine must take in the name of a galaxy and return it and the QSOs around it. 

def gal_model(galaxy): 

    cwd = os.getenv('LUVOIR_SIMTOOLS_DIR')

    if 'M51' in galaxy: 
        gal = {'name':'M51', 'ra':202.4842 * u.deg, 'dec':47.2306 * u.deg, 'distance':7.272 * u.Mpc, 
 			'url':'http://www.stsci.edu/~tumlinso/M51.jpg'} 
        galCoords = SkyCoord(gal['ra'], gal['dec'], unit=(u.hourangle, u.deg))
    if 'M87' in galaxy: 
        gal = {'name':'M87', 'ra':187.7059304 * u.deg, 'dec':12.3911231 * u.deg, 'distance':16.56 * u.Mpc, 
 			'url':'http://www.stsci.edu/~tumlinso/M87.jpg'} 
        galCoords = SkyCoord(gal['ra'], gal['dec'], unit=(u.hourangle, u.deg))
    if 'CenA' in galaxy: 
        print('sorry not yet') 

    dr7qso = QTable.read(cwd+'/data/dr7_qso_galex.fits')
    
    return gal, dr7qso 





