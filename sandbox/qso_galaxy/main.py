# coding: utf-8
# # Investigating QSOs near Cen A (NGC 5128)
# [Simbad Information for NGC 5128](http://simbad.u-strasbg.fr/simbad/sim-basic?Ident=cen+a&submit=SIMBAD+search)
import matplotlib.pyplot as plt
import numpy as np
from astropy.table import QTable
import astropy.units as u
from astropy.coordinates import SkyCoord # AstroPy treatment of coordinates
from astroquery.simbad import Simbad # SIMBAD query functionality 
import copy 
import os 

from bokeh.plotting import figure, gridplot, output_file, show
from bokeh.models import ColumnDataSource, Paragraph, Range1d
from bokeh.models.widgets import Panel, Tabs, Slider, Div, Button, DataTable, DateFormatter, TableColumn 
from bokeh.io import curdoc
from bokeh.models.widgets import Select 

import qso_model as q 

cwd = os.getenv('LUVOIR_SIMTOOLS_DIR')

xqso, yqso, mags = q.qso_model() 
qso_points = ColumnDataSource(data={'xqso':xqso, 'yqso':-1.*yqso, 'x':xqso, 'y':-1.*yqso, 'mag':mags}) 

image1 = "http://www.stsci.edu/~tumlinso/cenA-Fermi-noLabel.jpg" 
p1 = figure(x_range=[0, 586], y_range=[-786, 0], title='Cen A', \
    tools="pan,resize,save,box_zoom,wheel_zoom,reset",toolbar_location='right') 
    
p1.background_fill_color = "white"
p1.image_url(url=[image1], x=[0], y=[0], w=586, h=795, global_alpha=0.95)
p1.x_range = Range1d(0, 586, bounds=(0, 586))  
p1.y_range = Range1d(-795, 0, bounds=(-795,0))
p1.circle('x', 'y', source=qso_points, fill_color='#FFCC66', size=8)

lookup = {'3.0':18.0, '3':18.0, '6.0':19.2, '6':19.2, '9.0':20.1, '9':20.1, '12':21.0, '12.0':21.0, '15.0':21.8, '15':21.8} 

def update_image(attr,old,new): 
    ####there is some real stupid CDS bullshit here. 
    maglimit = lookup[str(aperture.value)]
    print 'will now cut by maglimit: ', maglimit 
    imag = (qso_points.data['mag'] > maglimit)  
    xx = copy.deepcopy(xqso) 
    xx[imag] = xx[imag] + 10000. 
    print xx[imag]
    qso_points.data['x'] = xx 


aperture= Slider(title="Aperture (meters)", value=15., start=3., end=15.0, step=3.0, callback_policy='mouseup', width=500)
aperture.on_change('value', update_image) 
adf = gridplot([aperture], [p1]) 

curdoc().add_root(adf)

