import numpy as np
import matplotlib.image as mpimg
from astropy.table import Table 
from bokeh.plotting import Figure, gridplot, output_file, show
from bokeh.models import ColumnDataSource, HBox, VBoxForm, Paragraph, Range1d
from bokeh.io import curdoc
from bokeh.models.widgets import Select, CheckboxButtonGroup, CheckboxGroup
from bokeh.models import NumeralTickFormatter
from __future__ import print_function



mjup = 317.8 

p1 = Figure(x_range=[0.003, 3000], y_range=[0.01, 30000], tools="pan,save,wheel_zoom,reset",toolbar_location='above', \
			title=' ', y_axis_type="log", x_axis_type='log', plot_height=400, plot_width=800) 
p1.background_fill_color = "white"
p1.patch([0.003, 1.0, 0.2, 0.003, 0.003], [1, 20, 30000., 30000., 1.], alpha=0.5, fill_color='pink', line_width=0)
p1.patch([0.003, 0.04, 0.04, 0.003, 0.003], [100, 100, 30000., 30000., 10000.], alpha=0.6, fill_color='lightblue', line_width=0)
p1.patch([3, 3000, 3000, 30, 3], [300, 300, 30000., 30000., 300.], alpha=0.6, fill_color='purple', line_width=0)
p1.yaxis.axis_label = 'Planet Mass / Earth' 
p1.xaxis.axis_label = 'Semi-major Axis / Snow Line' 
p1.xaxis.axis_label_text_font_style = 'bold' 
p1.yaxis.axis_label_text_font_style = 'bold' 
p1.xaxis[0].formatter = NumeralTickFormatter(format="0.00")
p1.x_range = Range1d(0.003, 3000, bounds=(0.003, 3000))  
p1.y_range = Range1d(0.01, 30000, bounds=(0.01,30000))

techniques = ['RV', 'Space Transits', 'Ground Transits', 'Microlensing', 'Direct Imaging'] 

checkbox_button_group = CheckboxGroup(labels=["RV", "Transits", "Microlensing", "Direct Imaging"], active=[0, 1, 2, 3])

# transits - ground 
tground = Table.read('/Users/tumlinson/Dropbox/LUVOIR_STDT/luvoir_simtools/planetspace/transit_ground.dat', format='ascii', names=['name','msini','semi','mstar']) 
a_rad = 2.7 * tground['mstar'] 
tground_syms = p1.triangle(tground['semi']/a_rad, tground['msini'] * mjup, color='lightblue', fill_alpha=0.8, line_alpha=1., size=8) 

# transits - space  
tspace  = Table.read('/Users/tumlinson/Dropbox/LUVOIR_STDT/luvoir_simtools/planetspace/transit_space.dat', format='ascii', names=['name','msini','semi','mstar']) 
a_rad = 2.7 * tspace['mstar'] 
tground_syms = p1.diamond(tspace['semi']/a_rad, tspace['msini'] * mjup, color='darkblue', fill_alpha=0.4, line_alpha=1., size=8) 


# RV 
rv = Table.read('/Users/tumlinson/Dropbox/LUVOIR_STDT/luvoir_simtools/planetspace/rv.dat', format='ascii', names=['name','msini','semi','mstar']) 
a_rad = 2.7 * rv['mstar'] 
rv_syms = p1.circle(rv['semi']/a_rad, rv['msini'] * mjup, color='red', fill_alpha=0.4, line_alpha=1., size=8) 

# microlens 
ulens = Table.read('/Users/tumlinson/Dropbox/LUVOIR_STDT/luvoir_simtools/planetspace/ulens.dat', format='ascii', names=['name','msini','semi','mstar']) 
a_rad = 2.7 * ulens['mstar'] 
ulens_syms = p1.asterisk(ulens['semi']/a_rad, ulens['msini'] * mjup, color='green', size=8) 

# imaging 
ulens = Table.read('/Users/tumlinson/Dropbox/LUVOIR_STDT/luvoir_simtools/planetspace/imaging.dat', format='ascii', names=['name','msini','semi','mstar']) 
a_rad = 2.7 * ulens['mstar'] 
ulens_syms = p1.square(ulens['semi']/a_rad, ulens['msini'] * mjup, fill_alpha=0.4, line_alpha=0.9, color='purple', size=8) 


p1.text([5.2/2.7], [317.8], ['J'], text_color="red", text_align="center") 


#xyouts, 5.2/2.7, 317.8, 'J', align=0.5 
#xyouts, 9.6/2.7,  95.2, 'S', align=0.5 
#xyouts, 19.2/2.7,  14.5, 'U', align=0.5 
#xyouts, 30.1/2.7,  17.1, 'N', align=0.5 
#xyouts, 1.0/2.7,   1.0, 'E', align=0.5 
#xyouts, 0.72/2.7,   0.8, 'V', align=0.5 
#xyouts, 1.5/2.7,   0.1, 'M', align=0.5 
#xyouts, 0.39/2.7,   0.055, 'M', align=0.5 



def update_image(active): 
   print 'wHAT?'
   print active 
   print active.__contains__(1) 

p = gridplot([[p1, checkbox_button_group]]) 

checkbox_button_group.on_click(update_image) 
curdoc().add_root(p)


