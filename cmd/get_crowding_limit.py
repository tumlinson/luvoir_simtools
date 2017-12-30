import numpy as np 
import pandas as pd 
import astropy.units as u 

def get_crowding_limit(crowding_apparent_magnitude, distance, cmd_frame): 

    g_solar = 4.487 
    luvoir_stars_per_arcsec_limit = 100.  # (JD1) 

    distmod = 5. * np.log10((distance+1e-5) * 1e6) - 5.

    g = np.array(-1.0 * cmd_frame.gmag) # absolute magnitude in the g band - the -1 corrects for the sign flip in load_datasets (for plotting) 
    g.sort() 				# now sorted from brightest to faintest in terms of absolute g magnitude 
    luminosity = 10.**(-0.4 * (g - g_solar)) 
    total_luminosity_in_lsun = np.sum(luminosity) 
    total_mass_in_msun = np.sum(cmd_frame.Mass) 
    number_of_stars = g * 0.0 + 1.0     # initial number of stars in each "bin" - a list of 10,000 stars 

    total_absolute_magnitude = -2.5 * np.log10(total_luminosity_in_lsun) + g_solar 
    apparent_brightness_at_this_distance = total_absolute_magnitude + distmod 

    scale_factor = 10.**(-0.4*(crowding_apparent_magnitude - apparent_brightness_at_this_distance)) 

    cumulative_luminosity = np.cumsum(luminosity * scale_factor * number_of_stars) # the cumulative run of luminosity in Lsun 
    cumulative_app_magnitude = -2.5 * np.log10(cumulative_luminosity) + g_solar + distmod
    cumulative_number_of_stars = np.cumsum(scale_factor * number_of_stars) # the cumulative run of luminosity in Lsun 
    #for i in np.arange(np.size(g[0:500])): 
    #    print(i, g[i], cumulative_luminosity[i], cumulative_number_of_stars[i], cumulative_app_magnitude[i]) 

    crowding_limit = np.interp(luvoir_stars_per_arcsec_limit, cumulative_number_of_stars, g) 
  
    return crowding_limit 


mags = """ 
ACS_F435W       FLOAT           5.28100
ACS_F475W       FLOAT           5.02100
ACS_F555W       FLOAT           4.78400
ACS_F606W       FLOAT           4.68600
ACS_F625W       FLOAT           4.60500
ACS_F775W       FLOAT           4.49400
ACS_F814W       FLOAT           4.48700
ACS_F850LP      FLOAT           4.47400
UVIS_F218W      FLOAT           10.3620
UVIS_F225W      FLOAT           9.74700
UVIS_F275W      FLOAT           8.20900
UVIS_F336W      FLOAT           6.50200
UVIS_F390W      FLOAT           5.73500
UVIS_F438W      FLOAT           5.24000
UVIS_F475W      FLOAT           5.00400
UVIS_F555W      FLOAT           4.80800
UVIS_F606W      FLOAT           4.69100
UVIS_F775W      FLOAT           4.49500
UVIS_F814W      FLOAT           4.48800
"""
