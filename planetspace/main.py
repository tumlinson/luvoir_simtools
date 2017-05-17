import numpy as np
import matplotlib.image as mpimg
from astropy.table import Table 

from bokeh.plotting import figure, gridplot, output_file, show
from bokeh.models import ColumnDataSource, HBox, VBoxForm, Paragraph, Range1d
from bokeh.io import hplot, vplot, curdoc
from bokeh.models.widgets import Select, CheckboxButtonGroup, CheckboxGroup


image_to_use = Select(title="Image to See", value="Galaxy", options=["Galaxy (z=2)", "Deep Field", "Star Forming Region", "Perseus A", "Pluto"], width=200)
mjup = 317.8 

p1 = figure(x_range=[0.003, 3000], y_range=[0.01, 30000], tools="pan,resize,save,box_zoom,wheel_zoom,reset",toolbar_location='right', \
			title=' ', y_axis_type="log", x_axis_type='log')
p1.background_fill_color = "white"

checkbox_button_group = CheckboxGroup(
        labels=["RV", "Transits", "Microlensing", "Direct Imaging"], active=[0, 1, 2, 3])

# RV 
rv = Table.read('/Users/tumlinson/Dropbox/LUVOIR_STDT/luvoir_simtools/planetspace/rv.dat', format='ascii', names=['name','msini','semi','mstar']) 
a_rad = 2.7 * rv['mstar'] 
rv_syms = p1.circle(rv['semi']/a_rad, rv['msini'] * mjup, color='red', fill_alpha=0.6, line_alpha=1., size=10) 

# microlens 
ulens = Table.read('/Users/tumlinson/Dropbox/LUVOIR_STDT/luvoir_simtools/planetspace/ulens.dat', format='ascii', names=['name','msini','semi','mstar']) 
a_rad = 2.7 * ulens['mstar'] 
ulens_syms = p1.asterisk(ulens['semi']/a_rad, ulens['msini'] * mjup, color='green', size=9) 

# imaging s 
ulens = Table.read('/Users/tumlinson/Dropbox/LUVOIR_STDT/luvoir_simtools/planetspace/imaging.dat', format='ascii', names=['name','msini','semi','mstar']) 
a_rad = 2.7 * ulens['mstar'] 
ulens_syms = p1.square(ulens['semi']/a_rad, ulens['msini'] * mjup, color='purple', size=9) 

def update_image(active): 
   print 'wHAT?'
   print active 

p = gridplot([[checkbox_button_group, p1]]) 

checkbox_button_group.on_click(update_image) 

curdoc().add_root(p)
