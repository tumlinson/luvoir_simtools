
; this code opens all the Stark yield files to obtain the largest possible list of targets therein
; the resulting fits file should be used to construct the other derived products 

spawn, "ls -l *sav | awk '{print $9}' > idlsaves" 
readcol, 'idlsaves', filename, format='A' 

polar_coords = fltarr(2, 125000) 
r = fltarr(1, 125000) 
theta = fltarr(1, 125000) 
hip = fltarr(1, 125000) 
distance = fltarr(1, 125000) 
type = strarr(1, 125000) 
ra = fltarr(1, 125000) 
dec = fltarr(1, 125000) 

for i = 0, n_elements(filename)-1 do begin 

 restore, filename[i] 
 d = fix(d) 
 nexozodis = fix(nexozodis) 
 print, filename[i], eta_earth, d, contrast, iwafactor, nexozodis, nstars, nplanets

 for ir = 0, n_elements(target_list.ra)-1 do begin 
    r[0, target_list[ir].hip] = target_list[ir].dist 
    theta[0, target_list[ir].hip] = target_list[ir].ra / 360. * 2. * !pi 
    polar_coords[0,target_list[ir].hip] = target_list[ir].ra / 360. * 2. * !pi 
    polar_coords[1,target_list[ir].hip] = target_list[ir].dist 
    hip[0,target_list[ir].hip] = target_list[ir].hip 
    distance[0, target_list[ir].hip] = target_list[ir].dist 
    type[0,target_list[ir].hip] = target_list[ir].type 
    ra[0,target_list[ir].hip] = target_list[ir].ra
    dec[0,target_list[ir].hip] = target_list[ir].dec  
 endfor 

endfor 

 xx_yy = cv_coord(from_polar=polar_coords, /to_rect)  
 x = xx_yy[0,*] 
 y = xx_yy[1,*] 

 itarg = where(hip gt 0) 
 x = x[itarg] 
 y = y[itarg] 
 distance = distance[itarg] 
 type = type[itarg] 
 ra = ra[itarg] 
 dec = dec[itarg] 
 hip = hip[itarg] 

 targets = {ra:ra, dec:dec, x:x, y:y, distance:distance, hip:hip, type:type} 
 spawn, "rm stark_targets.fits" 
 mwrfits, targets, 'stark_targets.fits' 


end 
