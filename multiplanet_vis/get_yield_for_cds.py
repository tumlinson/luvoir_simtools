
from numpy import where 
from astropy.table import Table 
import copy 
import os 

def get_yield(aperture_in, contrast_in): 
    # this helper routine takes in an aperture, contrast combination and 
    # returns a dictionary that will go into a CDS 

    cwd = os.getenv('LUVOIR_SIMTOOLS_DIR')

    apertures = {'4.0':'4.0','4':'4.0','8':'8.0','8.0':'8.0','12':'12.0','12.0':'12.0',\
                 '14.0':'14.0','16':'16.0','20':'20.0','20.0':'20.0'} 
    contrasts = {'-11':'1.00E-11','-10':'1.00E-10','-9':'1.00E-09'} 
    filename = cwd+'multiplanet_vis/data/stark_multiplanet/'+'run_'+apertures[str(aperture_in)]+'_'+contrasts[str(contrast_in)]+'_0.10_3.0.fits' 
    targets = Table.read(filename) 
 
    col = copy.deepcopy(targets['TYPE'][0])
    col[:] = 'black'
    col[where(targets['COMPLETE1'][0] > 0.01*0.1)] = 'gold' # 'red'
    col[where(targets['COMPLETE1'][0] > 0.2*0.1)] = 'gold' # 'red'
    col[where(targets['COMPLETE1'][0] > 0.5*0.1)] = 'gold' # 'yellow'
    col[where(targets['COMPLETE1'][0] > 0.8*0.1)] = 'gold' # 'lightgreen'
    
    alp = copy.deepcopy(targets['TYPE'][0])
    alp[:] = 0.0  
    alp[where(targets['COMPLETE1'][0] > 0.01*0.1)] = 0.05 
    alp[where(targets['COMPLETE1'][0] > 0.2*0.1)] = 0.1
    alp[where(targets['COMPLETE1'][0] > 0.5*0.1)] = 0.3
    alp[where(targets['COMPLETE1'][0] > 0.8*0.1)] = 0.6
    
    # x0,y0 = original positons; x,y = positions that will be modified to hide C = 0 stars in view 
    xx = copy.deepcopy(targets['X'][0]) 
    xx[col == 'black'] = xx[col == 'black'] + 2000. 

    return  dict(x0 = targets['X'][0], \
                y0 = targets['Y'][0], \
                x  = xx, \
                y  = targets['Y'][0], \
                r  = targets['DISTANCE'][0], \
                hip=targets['HIP'][0], \
                stype=targets['TYPE'][0], \
                tspec=targets['TSPEC'][0], \
                color=col, \
                alpha=alp, \
                complete0=targets['COMPLETE0'][0], \
                complete1=targets['COMPLETE1'][0], \
                complete2=targets['COMPLETE2'][0], \
                complete3=targets['COMPLETE3'][0], \
                complete4=targets['COMPLETE4'][0], \
                complete5=targets['COMPLETE5'][0], \
                complete6=targets['COMPLETE6'][0], \
                complete7=targets['COMPLETE7'][0], \
                complete8=targets['COMPLETE8'][0], \
                ) 
