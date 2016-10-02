

targets = mrdfits('stark_targets.fits',1) 

apertures = [4., 8., 12., 12., 16., 20.] 
contrasts=[1e-11, 1e-10, 1e-09] 

for iap = 0, n_elements(apertures)-1 do begin 
     aperture = apertures[iap] 
  for icon = 0, n_elements(contrasts)-1 do begin 
     contrast = contrasts[icon] 
     
     aperture_string=strcompress(string(aperture, format='(F4.1)'),/remove_al) 
     contrast_string = string(contrast, format='(E8.2)')
     
     restore, 'tumlinson-full_results-'+aperture_string+'_'+contrast_string+'_3.0_0.10_5.0.sav' 
     
     completeness = fltarr(125000) ; create a variable that will hold total completeness for each star 
      
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
     
     for iobs = 0, n_elements(observations.c)-1 do begin 
       completeness[observations[iobs].hip] = completeness[observations[iobs].hip] + observations[iobs].c 
       print, iobs, observations[iobs].hip, observations[iobs].c, completeness[observations[iobs].hip] 
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
     
     this_run = {aperture:aperture, contrast:contrast, hip:hip, ra:ra, dec:dec, x:x, y:y, type:type, distance:distance, completeness:completeness} 
     
     outfilename = 'run_'+aperture_string+'_'+contrast_string+'_3.0_0.10_5.0.fits' 
     
     mwrfits, this_run, outfilename 

 endfor 
endfor 








end 


