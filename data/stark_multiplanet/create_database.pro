

targets = mrdfits('stark_targets.fits',1) 

apertures = [2., 4., 6., 8., 10., 12., 14., 16.] 
contrasts=[1e-10] 


for iap = 0, n_elements(apertures)-1 do begin 
     aperture = apertures[iap] 
  for icon = 0, n_elements(contrasts)-1 do begin 
     contrast = contrasts[icon] 
     
     aperture_string=strcompress(string(aperture, format='(F4.1)'),/remove_al) 
     contrast_string = string(contrast, format='(E8.2)')

     restore, 'tumlinson-multiplanet_results-'+aperture_string+'_'+contrast_string+'_3.6_0.1_3.0.sav' 
     
     completeness = fltarr(125000) ; create a variable that will hold total EARTH completeness for each star - same as the single planet yields 
     mpcompleteness = fltarr(125000,9) ; create a variable that will hold the completeness for each of the nine planet types in the multiplanet yields 
     tspec = fltarr(125000) ; create a variable that will hold total spectroscopic characterization time 
      
     distance = fltarr(125000) ; create a variable that will hold total completeness for each star 
     distance[targets.hip] = targets.distance 
     ra = fltarr(125000)
     ra[targets.hip] = targets.ra 
     dec = fltarr(125000) 
     dec[targets.hip] = targets.dec 
     x = fltarr(125000) 
     x[targets.hip] = targets.x 
     y = fltarr(125000) 
     y[targets.hip] = targets.y 
     hip = fltarr(125000) 
     hip[targets.hip] = targets.hip 
     type = strarr(125000) 
     type[targets.hip] = targets.type 

     ; Stark 
     ; Note that the values in .c the values in the .mpc vector are now all yield numbers, 
     ; i.e. they are completeness TIMES eta.  That’s a fundamental change to my code than I’ve permanently made.
     
     for iobs = 0, n_elements(mpobservations.c)-1 do begin 
       completeness[mpobservations[iobs].hip] = completeness[mpobservations[iobs].hip] + mpobservations[iobs].c 
       mpcompleteness[mpobservations[iobs].hip,*] = mpcompleteness[mpobservations[iobs].hip,*] + mpobservations[iobs].mpc 
       tspec[mpobservations[iobs].hip] = tspec[mpobservations[iobs].hip] + mpobservations[iobs].tspec / mpobservations[iobs].c
       
       print, iobs, mpobservations[iobs].hip, mpobservations[iobs].c, completeness[mpobservations[iobs].hip] 
     endfor 
     
     ihip = where(hip gt 0) 
     ra = ra[ihip] 
     dec = dec[ihip] 
     x = x[ihip] 
     y = y[ihip] 
     type = type[ihip] 
     distance = distance[ihip] 
     hip = hip[ihip] 
     completeness = completeness[ihip] 
     mpcompleteness = mpcompleteness[ihip,*] 
     tspec = tspec[ihip] 
     
     this_run = {aperture:aperture, contrast:contrast, hip:hip, ra:ra, dec:dec, x:x, y:y, type:type, $ 
                 distance:distance, completeness:completeness, mpcompleteness:mpcompleteness, tspec:tspec, eta_planet0:eta_planet0, sc_r0:sc_r0, $ 
		 sc_snr0:sc_snr0, mp_albedo:mp_albedo, mp_amin:mp_amin, mp_amax:mp_amax, mp_eta:mp_eta, mp_rmin:mp_rmin, $ 
	         mp_rmax:mp_rmax} 
     
     outfilename = 'run_'+aperture_string+'_'+contrast_string+'_3.6_0.1_3.0.fits' 
     
     mwrfits, this_run, outfilename

 endfor 
endfor 








end 


