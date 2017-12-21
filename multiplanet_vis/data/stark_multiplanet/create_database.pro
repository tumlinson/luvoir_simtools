
targets = mrdfits('stark_targets.fits',1) 

apertures = [4., 8., 12., 16., 20.] 
contrasts=[1e-11, 1e-10, 1e-9] 

for iap = 0, n_elements(apertures)-1 do begin 
     aperture = apertures[iap] 
  for icon = 0, n_elements(contrasts)-1 do begin 
     contrast = contrasts[icon] 
     
     aperture_string=strcompress(string(aperture, format='(F4.1)'),/remove_al) 
     contrast_string = string(contrast, format='(E8.2)')

     filename = 'kopparapu-multiplanet_results-'+aperture_string+'_'+contrast_string+'_0.24_3.0.sav' 
     print, filename 
     restore, filename 
     
     completeness = fltarr(125000) ; create a variable that will hold total EARTH completeness for each star - same as the single planet yields 
     mpcompleteness = fltarr(125000,15) ; create a variable that will hold the completeness for each of the nine planet types in the multiplanet yields 
     complete0 = fltarr(125000) 
     complete1 = fltarr(125000) 
     complete2 = fltarr(125000) 
     complete3 = fltarr(125000) 
     complete4 = fltarr(125000) 
     complete5 = fltarr(125000) 
     complete6 = fltarr(125000) 
     complete7 = fltarr(125000) 
     complete8 = fltarr(125000) 
     complete9 = fltarr(125000) 
     complete10= fltarr(125000) 
     complete11= fltarr(125000) 
     complete12= fltarr(125000) 
     complete13= fltarr(125000) 
     complete14= fltarr(125000) 
     tspec = fltarr(125000) ; create a variable that will hold total spectroscopic characterization time 
      
     distance = fltarr(125000) ; create a variable that will hold total completeness for each star 
     distance[targets.starid] = targets.distance 
     ra = fltarr(125000)
     ra[targets.starid] = targets.ra 
     dec = fltarr(125000) 
     dec[targets.starid] = targets.dec 
     x = fltarr(125000) 
     x[targets.starid] = targets.x 
     y = fltarr(125000) 
     y[targets.starid] = targets.y 
     starid = fltarr(125000) 
     starid[targets.starid] = targets.starid 
     type = strarr(125000) 
     type[targets.starid] = targets.type 

     ; Stark 
     ; Note that the values in .c the values in the .mpc vector are now all yield numbers, 
     ; i.e. they are completeness TIMES eta.  That’s a fundamental change to my code than I’ve permanently made.
     
     for iobs = 0, n_elements(mpobservations.c)-1 do begin 
       completeness[mpobservations[iobs].starid] = completeness[mpobservations[iobs].starid] + mpobservations[iobs].c 
       tspec[mpobservations[iobs].starid] = tspec[mpobservations[iobs].starid] + mpobservations[iobs].tspec / mpobservations[iobs].c

       mpcompleteness[mpobservations[iobs].starid,*] = mpcompleteness[mpobservations[iobs].starid,*] + mpobservations[iobs].mpc 

       complete0[mpobservations[iobs].starid] = complete0[mpobservations[iobs].starid] + mpobservations[iobs].mpc[0] 
       complete1[mpobservations[iobs].starid] = complete1[mpobservations[iobs].starid] + mpobservations[iobs].mpc[1] 
       complete2[mpobservations[iobs].starid] = complete2[mpobservations[iobs].starid] + mpobservations[iobs].mpc[2] 
       complete3[mpobservations[iobs].starid] = complete3[mpobservations[iobs].starid] + mpobservations[iobs].mpc[3] 
       complete4[mpobservations[iobs].starid] = complete4[mpobservations[iobs].starid] + mpobservations[iobs].mpc[4] 
       complete5[mpobservations[iobs].starid] = complete5[mpobservations[iobs].starid] + mpobservations[iobs].mpc[5] 
       complete6[mpobservations[iobs].starid] = complete6[mpobservations[iobs].starid] + mpobservations[iobs].mpc[6] 
       complete7[mpobservations[iobs].starid] = complete7[mpobservations[iobs].starid] + mpobservations[iobs].mpc[7] 
       complete8[mpobservations[iobs].starid] = complete8[mpobservations[iobs].starid] + mpobservations[iobs].mpc[8] 
       complete9[mpobservations[iobs].starid] = complete9[mpobservations[iobs].starid] + mpobservations[iobs].mpc[9] 
       complete10[mpobservations[iobs].starid] = complete10[mpobservations[iobs].starid] + mpobservations[iobs].mpc[10] 
       complete11[mpobservations[iobs].starid] = complete11[mpobservations[iobs].starid] + mpobservations[iobs].mpc[11] 
       complete12[mpobservations[iobs].starid] = complete12[mpobservations[iobs].starid] + mpobservations[iobs].mpc[12] 
       complete13[mpobservations[iobs].starid] = complete13[mpobservations[iobs].starid] + mpobservations[iobs].mpc[13] 
       complete14[mpobservations[iobs].starid] = complete14[mpobservations[iobs].starid] + mpobservations[iobs].mpc[14] 
       
       print, iobs, mpobservations[iobs].starid, mpobservations[iobs].mpc
      
     endfor 
     
     istarid = where(starid gt 0) 
     ra = ra[istarid] 
     dec = dec[istarid] 
     x = x[istarid] 
     y = y[istarid] 
     type = type[istarid] 
     distance = distance[istarid] 
     starid = starid[istarid] 
     completeness = completeness[istarid] 
     mpcompleteness = mpcompleteness[istarid,*] 
     complete0 = complete0[istarid] 
     complete1 = complete1[istarid] 
     complete2 = complete2[istarid] 
     complete3 = complete3[istarid] 
     complete4 = complete4[istarid] 
     complete5 = complete5[istarid] 
     complete6 = complete6[istarid] 
     complete7 = complete7[istarid] 
     complete8 = complete8[istarid] 
     complete9 = complete9[istarid] 
     complete10 = complete10[istarid] 
     complete11 = complete11[istarid] 
     complete12 = complete12[istarid] 
     complete13 = complete13[istarid] 
     complete14 = complete14[istarid] 
     tspec = tspec[istarid] 
     
     this_run = {aperture:aperture, contrast:contrast, starid:starid, ra:ra, dec:dec, x:x, y:y, type:type, $ 
                 distance:distance, completeness:completeness, mpcompleteness:mpcompleteness, tspec:tspec, $ 
                 eta_planet0:eta_planet0, sc_r0:sc_r0, $ 
		 sc_snr0:sc_snr0, mp_amin:mp_amin, mp_amax:mp_amax, mp_eta:mp_eta, mp_rmin:mp_rmin, $ 
                 complete0:complete0, complete1:complete1, complete2:complete2, complete3:complete3, complete4:complete4, $ 
                 complete5:complete5, complete6:complete6, complete7:complete7, complete8:complete8, $ 
                 complete9:complete9, complete10:complete10, complete11:complete11, complete12:complete12, $ 
                 complete13:complete13, complete14:complete14, $ 
	         mp_rmax:mp_rmax} 
     
     outfilename = 'run_'+aperture_string+'_'+contrast_string+'_0.24_3.0.fits' 
     
     mwrfits, this_run, outfilename

 endfor 
endfor 








end 


