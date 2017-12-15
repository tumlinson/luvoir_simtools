# -*- coding: utf-8 -*-
"""
Created on Tue Mar 21 14:58:29 2017

@author: gkanarek
"""

import numpy as np
from scipy.fftpack import fft2, ifft2
from astropy.modeling.functional_models import Gaussian2D #our basic psf
import astropy.units as u
from scipy.ndimage import imread, zoom
from scipy.misc import imsave, imresize
from skimage.transform import pyramid_reduce

def gaussian_blur(image, aperture_from, aperture_to, wavelength):
    """
    Blur an image to a new aperture radius using Gaussian (de)convolution.
    """
    
    assert aperture_to < aperture_from #Can only blur, not sharpen, due to deconvolution theorem
    
    multichannel = image.ndim == 3 #multichannel image
    
    #Since we're using a Gaussian approximation to an Airy Disk, the RMS sigma of
    #the Gaussian is 0.42 * lambda / D
    sigma0 = (0.42 * wavelength / aperture_from).decompose()
    sigma1 = (0.42 * wavelength / aperture_to).decompose()
    
    if multichannel: #I believe this is the format for multichannel images.....
        nx, ny, channels = image.shape
    else:
        nx, ny = image.shape
    
    xcen = nx // 2
    ycen = ny // 2
    xpx, ypx = np.mgrid[:nx, :ny]
    
    #assume a circular PSF
    psf0 = Gaussian2D(amplitude=1., x_mean=xcen, y_mean=ycen, 
                      x_stddev=sigma0.value, y_stddev=sigma0.value)
    psf1 = Gaussian2D(amplitude=1., x_mean=xcen, y_mean=ycen,
                      x_stddev=sigma1.value, y_stddev=sigma1.value)
    
    kernel0 = psf0(xpx, ypx)
    kernel1 = psf1(xpx, ypx)
    
    fourier0 = fft2(kernel0)
    fourier1 = fft2(kernel1)
    
    blurred_img = np.zeros_like(image, dtype=float)
    
    if multichannel:
        for c in range(channels):
            fourier_img = fft2(image[..., c])
            blurred_img[..., c] = ifft2(fourier_img * fourier1 / fourier0)
    else:
        fourier_img = fft2(image)
        blurred_img = ifft2(fourier_img * fourier1 / fourier0)
    
    return blurred_img

    
if __name__ == "__main__":
    import os
    #import matplotlib.pyplot as plt
    os.chdir('/Users/gkanarek/Desktop/luvoir_simtools/image_comparison_gk/static')
    
    titles = ['Original', 'Gaussian blur', '(Linear) Zoom', 'Blur->Zoom', 'Zoom->Blur',
              'pyramid_reduce']
        
    
    #fjpg = "HDST_source_z2.jpg"
    fpng = "pretty.png"
    
    ap1 = 2.4 * u.m
    ap0 = 12.0 * u.m
    wave = 500 * u.nm
    
    px0 = (0.61 * u.rad * wave / ap0).to(u.arcsec)
    px1 = (0.61 * u.rad * wave / ap1).to(u.arcsec)
    
    pixel_scale = (px0 / px1).value
    downscale = (px1 / px0).value
    print("Pixel scale: {:8.5f}".format(pixel_scale))
    
    print("reading!")
    #jpg0 = imread(fjpg)
    png0 = imread(fpng)
    
    def show_fig(img, title, fname):
        if img.size < png0.size:
            out = imresize(img, downscale, interp='nearest')
        else:
            out = img
        imsave(fname, out)
        #f, ax = plt.subplots(figsize=(10,10))
        #ax.imshow(img, interpolation='none')
        #ax.axis('off')
        #ax.set_title(title)
        #f.savefig(fname, bbox_inches='tight')
    
    print("gaussian pt 1")
    #gjpg_pre = gaussian_blur(jpg0, ap0, ap1, wave)
    gpng_pre = gaussian_blur(png0, ap0, ap1, wave)
    show_fig(gpng_pre, titles[1], "imgmod_test_gauss.png")
    
    '''print("isolated zoom, linear")
    #zjpg = zoom(jpg0, (pixel_scale, pixel_scale, 1))
    zpng = zoom(png0, (pixel_scale, pixel_scale, 1), order=1)
    show_fig(zpng, titles[2], "imgmod_test_zoom.png")
    
    print("zoom post gaussian, linear")
    #zgjpg = zoom(gjpg_pre, (pixel_scale, pixel_scale, 1))
    zgpng = zoom(gpng_pre, (pixel_scale, pixel_scale, 1), order=1)
    show_fig(zgpng, titles[3], "imgmod_test_gauss_zoom.png")
    
    print("gaussian pt 2")
    #gjpg_post = gaussian_blur(zjpg, ap0, ap1, wave)
    gpng_post = gaussian_blur(zpng, ap0, ap1, wave)
    show_fig(gpng_post, titles[4], "imgmod_test_zoom_gauss.png")
    
    print("pyramid_reduce")
    #prjpg = pyramid_reduce(jpg0, downscale=downscale)
    prpng = pyramid_reduce(png0, downscale=downscale)
    show_fig(prpng, titles[5], "imgmod_test_pyramidreduce.png")
    
    """print("plotting")
    #fj, aj = plt.subplots(1, 6, figsize=(16, 2.5))
    #for i, img in [jpg0, gjpg_pre, zjpg, zgjpg, gjpg_post, prjpg]:
    #    aj[i].imshow(img, interpolation='none')
    #    aj[i].set_title(titles[i])
    #    aj[i].axis('off')
    
    #fj.savefig('imagemod_test.jpg', bbox_inches='tight')
    
    fp, ap = plt.subplots(1, 6, figsize=(16, 2.5))
    for i, img in enumerate([png0, gpng_pre, zpng, zgpng, gpng_post, prpng]):
        ap[i].imshow(img, interpolation='none')
        ap[i].set_title(titles[i])
        ap[i].axis('off')
    
    fp.savefig('imagemod_test.png', bbox_inches='tight')"""'''
    
    
    