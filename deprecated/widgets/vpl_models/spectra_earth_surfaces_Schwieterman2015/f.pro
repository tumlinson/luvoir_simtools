

;readcol, 'earth_clearsky_hitran08_8333_100000cm_bacterialmat_60sza_toa.rad', wave, waven, star_bacteria, bacteria 
;readcol, 'earth_clearsky_hitran08_8333_100000cm_conifers_60sza_toa.rad', wave, waven, star_conifers, conifers 
;readcol, 'earth_clearsky_hitran08_8333_100000cm_grass_60sza_toa.rad', wave, waven, star_grass, grass 
;readcol, 'earth_clearsky_hitran08_8333_100000cm_gypsum_60sza_toa.rad', wave, waven, star_gypsum, gypsum 
;readcol, 'earth_clearsky_hitran08_8333_100000cm_halite_60sza_toa.rad', wave, waven, star_halite, halite 
;readcol, 'earth_clearsky_hitran08_8333_100000cm_ocean_60sza_toa.rad', wave, waven, star_ocean, ocean 
;readcol, 'earth_clearsky_hitran08_8333_100000cm_redalgae_60sza_toa.rad', wave, waven, star_redalgae, redalgae 
;readcol, 'earth_clearsky_hitran08_8333_100000cm_snow_60sza_toa.rad', wave, waven, star_snow, snow 
;readcol, 'earth_clearsky_hitran08_8333_100000cm_halophile_60sza_toa.rad', wave, waven, star_halophile, halophile 

bin = 3000 

restore, 'spectra_idl.dat' 
wave = frebin(wave,bin) 
snow = frebin(snow  / star_snow, bin) 
redalgae = frebin(redalgae  / star_redalgae, bin) 
grass = frebin(grass  / star_grass, bin) 
gypsum = frebin(gypsum  / star_gypsum, bin) 
conifers = frebin(conifers  / star_conifers, bin) 
ocean = frebin(ocean  / star_ocean, bin) 
bacteria = frebin(bacteria  / star_bacteria, bin) 
halophile = frebin(halophile  / star_halophile, bin) 
halite = frebin(halite  / star_halite, bin) 

spec1 = 0.2 * (redalgae) + 0.5 * (snow) + 0.3 * (grass)
spec2 = 0.2 * (ocean) + 0.6 * (conifers) + 0.1 * (bacteria) + 0.1 * (gypsum)
spec3 = 0.4 * (halite) + 0.3 * (ocean) + 0.3 * (halophile)


psopen, 'a.ps', /encap, xs=8, ys=4, /inches 
loadct, 0  
plot, [0], [0], xrange=[0.4, 1.2], yrange=[0, 0.6], xtitle='Wavelength [micron]', ytitle='Reflectance' 
loadct, 13 
loadct, 0  
oplot, wave, spec2, thick=2, color=180 
oplot, wave, spec3, thick=2, color=180 
oplot, wave, spec1, thick=4 
psclose, /nos  
spawn, '/Users/tumlinson/Dropbox/COS-Halos/idl/bin/idlepstopdf.sh a.ps' 

psopen, 'b.ps', /encap, xs=8, ys=4, /inches 
loadct, 0  
plot, [0], [0], xrange=[0.4, 1.2], yrange=[0, 0.6], xtitle='Wavelength [micron]', ytitle='Reflectance' 
loadct, 13 
loadct, 0  
oplot, wave, spec1, thick=2, color=180 
oplot, wave, spec3, thick=2, color=180 
oplot, wave, spec2, thick=4
psclose, /nos  
spawn, '/Users/tumlinson/Dropbox/COS-Halos/idl/bin/idlepstopdf.sh b.ps' 

psopen, 'c.ps', /encap, xs=8, ys=4, /inches 
loadct, 0  
plot, [0], [0], xrange=[0.4, 1.2], yrange=[0, 0.6], xtitle='Wavelength [micron]', ytitle='Reflectance' 
loadct, 13 
loadct, 0  
oplot, wave, spec1, thick=2, color=180 
oplot, wave, spec2, thick=2, color=180 
oplot, wave, spec3, thick=4
psclose, /nos  
spawn, '/Users/tumlinson/Dropbox/COS-Halos/idl/bin/idlepstopdf.sh c.ps' 

master_table = {wave:wave, snow:snow, algae:redalgae, grass:grass, gypsum:gypsum, conifers:conifers, ocean:ocean, bacteria:bacteria, halophile:halophile, halite:halite} 

mwrfits,master_table, 'master_table.fits'  
