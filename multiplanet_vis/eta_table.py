

def eta_table(): 
    eta_tab = dict(ptype=['Hot Rocky', 'Warm Rocky', 'Cold Rocky', 
               'Hot SuperEarths', 'Warm SuperEarths', 'Cold SuperEarths',
               'Hot SubNeptunes', 'Warm SubNeptunes','Cold SubNeptunes',
               'Hot Neptunes', 'Warm Neptunes', 'Cold Neptunes',
               'Hot Jupiters','Warm Jupiters','Cold Jupiters'],
        radii=['0.5-1.0','0.5-1.0','0.5-1.0',
               '1.-1.75','1.-1.75','1.-1.75',
               '1.75-3.5','1.75-3.5','1.75-3.5',
               '3.5-6','3.5-6','3.5-6',
               '6-14.3','6-14.3','6-14.3'],
        eta=['0.68','0.30','1.6',
             '0.47','0.21','1.16', 
             '0.48','0.22','1.33', 
             '0.078','0.074','0.95', 
             '0.048','0.045','0.58'],  
        a = ['0.74-0.97','0.97-1.86','1.86-17.7',
             '0.073-0.94','0.94-1.80','1.80-18.26', 
             '0.070-0.85','0.85-1.62','1.62-18.26',
             '0.067-0.78','0.78-1.54','1.54-19.24',
             '0.067-0.77','0.77-1.54','1.54-20.']
         )
    return eta_tab 
