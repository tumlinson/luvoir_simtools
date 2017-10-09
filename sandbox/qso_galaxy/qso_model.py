# coding: utf-8
import matplotlib.pyplot as plt
import numpy as np
from astropy.table import QTable
import astropy.units as u
from astropy.coordinates import SkyCoord # AstroPy treatment of coordinates
from astroquery.simbad import Simbad # SIMBAD query functionality 
import os 

def qso_model(): 

    cwd = os.getenv('LUVOIR_SIMTOOLS_DIR')

    #### Grab Cen A information from SIMBAD eventually the galaxy will be a user choice 
    cenA = Simbad.query_object('ngc5128')
    cenAdistance = 3.8 * u.Mpc  # Harris et al. (2010)
    cenACoords = SkyCoord(cenA['RA'][0], cenA['DEC'][0], unit=(u.hourangle, u.deg))
    
    imCenA = plt.imread(cwd+'/data/cenA-Fermi-noLabel.jpg')
    imCenA = imCenA[:,0:556,:]
    
    # Work out angle for FoV on the sky. The "scale" is based on a measurement with
    # a different image, so need to get that scale right (all the bits at the end).
    scale = 300.*u.kpc / (595*786./1007) # kpc/pixel
    FoV = np.array(np.shape(imCenA)[0:-1])
    FoV = FoV[[1,0]]
    FoV_kpc = FoV * scale
    angle = np.rad2deg(np.arctan(FoV_kpc / cenAdistance.to('kpc'))  )
    area = angle[0]*angle[1]                  # x * y
    
    dr7qso = QTable.read(cwd+'/data/dr7_qso_galex.fits')
    zem = dr7qso['Z'][0]
    fuv = dr7qso['FUV_MAG'][0]
    nuv = dr7qso['NUV_MAG'][0]
    
    # these limiting mags correspond to the apertures Howk used 
    limitingmags = [18.0,19.2,20.1,21.0,21.8]
    numQSOs = np.zeros_like(limitingmags)
    for j in np.arange(np.size(limitingmags)):
        num = ((fuv > 10) & (fuv < limitingmags[j]))
        num = num.sum()
        numQSOs[j] += num
        
    numQSOs = np.array(numQSOs)/np.max(numQSOs) # Make this a relative number:
    qso_density_ref = 5./u.deg**2   # Rough QSO density = 5 for 15-m
    num_qsos = qso_density_ref * numQSOs[j] * area
    xqso=np.random.randint(0,FoV[0],size=num_qsos)
    yqso=np.random.randint(0,FoV[1],size=num_qsos)
    print 'numQSOs', numQSOs  
    # need to randomly generate mags too. . . . 
    mags = 3.8 * np.random.rand(num_qsos) + 18. 
  
    return xqso, yqso, mags 





