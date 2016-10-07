
import numpy as np 
import astropy.constants as const

def compute_snr(aperture, exposure_in_hours, ab_magnitudes):

    diff_limit = 1.22*(500.*0.000000001)*206264.8062/aperture
    print 'diff_limit', diff_limit

    pixel_size = np.array([0.016, 0.016, 0.016, 0.016, 0.016, 0.016, 0.016, 0.04, 0.04, 0.04])

    source_magnitudes = np.array([1., 1., 1., 1., 1., 1., 1.]) * ab_magnitudes
    central_wavelength = np.array([155., 228., 360., 440., 550., 640., 790., 1260., 1600., 2220.])
    ab_zeropoint = np.array([35548., 24166., 15305., 12523., 10018., 8609., 6975., 4373., 3444., 2482.])
    total_qe = np.array([0.1, 0.1, 0.15, 0.45, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6])
    aperture_correction = np.array([1., 1., 1., 1., 1., 1., 1., 1., 1., 1.])
    bandpass_r = np.array([5., 5., 5., 5., 5., 5., 5., 5., 5., 5.])
    derived_bandpass = central_wavelength / bandpass_r
    # two efficiency factors omitted

    detector_read_noise = np.array([3., 3., 3., 3., 3., 3., 3., 4., 4., 4.])
    dark_current = np.array([0.0005, 0.0005, 0.001, 0.001, 0.001, 0.001, 0.001, 0.002, 0.002, 0.002])
    sky_brightness = np.array([23.807, 25.517, 22.627, 22.307, 21.917, 22.257, 21.757, 21.567, 22.417, 22.537])
    fwhm_psf = 1.22 * central_wavelength * 0.000000001 * 206264.8062 / aperture
    fwhm_psf[fwhm_psf < diff_limit] = fwhm_psf[fwhm_psf < diff_limit] * 0.0 + diff_limit

    sn_box = np.round(3. * fwhm_psf / pixel_size)

    number_of_exposures = np.array([3., 3., 3., 3., 3., 3., 3., 3., 3., 3.])

    desired_exposure_time = np.array([1., 1., 1., 1., 1., 1., 1., 1., 1., 1.]) * exposure_in_hours * 3600.

    time_per_exposure = desired_exposure_time / number_of_exposures

    signal_counts = total_qe * desired_exposure_time * ab_zeropoint * aperture_correction * 0.7854 * \
        (aperture * 100.0)**2 * derived_bandpass * 10.**(-0.4*ab_magnitudes)

    shot_noise_in_signal = signal_counts ** 0.5

    sky_counts = total_qe * desired_exposure_time * ab_zeropoint * np.pi / 4. * (aperture * 100.0)**2 * \
        derived_bandpass * 10.**(-0.4*sky_brightness) * (pixel_size * sn_box)**2

    shot_noise_in_sky = sky_counts ** 0.5

    read_noise = detector_read_noise * sn_box * number_of_exposures**0.5

    dark_noise = sn_box * (dark_current * desired_exposure_time)**0.5

    thermal_counts = desired_exposure_time * C_thermal(central_wavelength, bandpass_r, sn_box**2, pixel_size, total_qe, aperture, 270., 0.09)  

    snr = signal_counts / (signal_counts + sky_counts + read_noise**2 + dark_noise**2 + thermal_counts)**0.5


    print
    print
    print
    print 'temperature', 270.
    print 'source_mag', source_magnitudes
    print 'central wave', central_wavelength
    print 'ab zeropoints', ab_zeropoint
    print 'total_qe', total_qe
    print 'ap corr', aperture_correction
    print 'bandpass R', bandpass_r
    print 'derived_bandpass', derived_bandpass
    print 'read_noise', detector_read_noise
    print 'dark rate', dark_current
    print 'sky_brightness', sky_brightness
    print 'fwhm_psf', fwhm_psf
    print 'sn_box', sn_box
    print 'number_of_exposures', number_of_exposures
    print 'detector_read_noise', detector_read_noise
    print 'time_per_exp', time_per_exposure
    print 'signal_counts', signal_counts
    print 'shot_noise_in_signal', shot_noise_in_signal
    print 'sky_counts', sky_counts
    print 'shot_noise_in_sky', shot_noise_in_sky
    print 'read noise', read_noise
    print 'dark noise', dark_noise
    print 'thermal counts ', thermal_counts 
    print 'SNR', snr, np.max(snr)
    print
    print
    print

    return snr


def C_thermal(wavelength_in_nm, R_bandwidth, N_pix, pixel_scale, QE_tot, D_in_meters, temperature, epsilon_T): 

    # Needs inputs:
    #   - wavelength in nm 
    #   - R value - "resolution" of bandwidth 
    #   - Telescope diameter D in meters 
    #   - telescope temperature 
    #   - epsilon_T = thermal emissivity for telescope (0.1 is a good number, or 0.09 for a TMA) 
    #   - QE_tot = pixel QE 
    #   - N_pix = number of pixels in photometric extraction box. NOTE: this should be the square of the 1D size 
    #			that is, if you intend a 3x3 box, use N_pix = 9 here. 
    #   - pixel_scale = pixel size in arcsec 
    
    wavelength_in_cm = wavelength_in_nm * 1e-7 # convert nm to cm 
    bandwidth = wavelength_in_cm / R_bandwidth # still in cm

    epsilon_T = 0.09 

    h = const.h.to('erg s').value # Planck's constant erg s 
    c = const.c.to('cm/s').value # speed of light [cm / s] 

    energy_per_photon = h * c / wavelength_in_cm 

    D = D_in_meters * 100. # telescope diameter in cm 

    Omega = 2.3504e-11 * pixel_scale**2 * N_pix 

    print 'Planck: ', planck(wavelength_in_cm, temperature) 
    print 'QE * Planck / E_per_phot', QE_tot * planck(wavelength_in_cm, temperature) / energy_per_photon 
    print 'E_per_phot', energy_per_photon 
    print 'Omega', Omega 

    C_thermal = epsilon_T * planck(wavelength_in_cm, temperature) / energy_per_photon * \
			(np.pi / 4. * D**2) * QE_tot * Omega * bandwidth 
 
    #print 'C_thermal', C_thermal 
  
    return C_thermal 
    

def planck(wave,temp):

    h=6.62606957e-27 # Planck's constant erg s 

    c=2.99792e10 # speed of light [cm / s] 

    k=1.3806488e-16 # Boltzmann's constant [erg deg K^-1] 

    x = 2. * h * c**2 / wave**5 

    exponent = (h * c / (wave * k * temp)) 
   
    PLANCK = x / (np.exp(exponent)-1.) 
    
    return PLANCK

