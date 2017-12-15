''' Docstring 
'''
import numpy as np
import math 
import copy 

from astropy.io import ascii 
from astropy.table import Table 

from bokeh.io import output_file, gridplot 
from bokeh.plotting import Figure
from bokeh.resources import CDN
from bokeh.embed import components 
from bokeh.models import ColumnDataSource, HBox, VBoxForm, HoverTool, Paragraph, Range1d 
from bokeh.layouts import Column, Row, WidgetBox
from bokeh.models.widgets import Slider, TextInput, Select 
from bokeh.io import hplot, vplot, curdoc
from bokeh.embed import file_html

el = Table.read('data/vpl_models/master_table.fits') 

first_spectrum = 0.1 * el['SNOW'][0] + 0.2 * el['CONIFERS'][0] + 0.1 * el['ALGAE'][0] + 0.6 * el['OCEAN'][0] 

snow0 = 0.1 * el['SNOW'][0] 
conifers0 = 0.2 * el['CONIFERS'][0] 
algae0 = 0.1 * el['ALGAE'][0] 
ocean0 = 0.6 * el['OCEAN'][0] 

full_spectrum = ColumnDataSource(data=dict(w=el['WAVE'][0], f=first_spectrum, snow=snow0, conifers=conifers0, algae=algae0, ocean=ocean0)) 

atm_plot = Figure(plot_height=400, plot_width=800, 
              tools="crosshair,hover,pan,reset,resize,save,box_zoom,wheel_zoom", outline_line_color='black', 
              x_range=[0.2, 1.2], y_range=[0, 0.5], toolbar_location='above') 

atm_plot.x_range=Range1d(0.2, 1.2, bounds=(0.2, 1.2)) 
atm_plot.y_range=Range1d(0.0, 0.5, bounds=(0.0, 0.5)) 

atm_plot.background_fill_color = "beige"
atm_plot.background_fill_alpha = 0.5 
atm_plot.yaxis.axis_label = 'Reflectivity' 
atm_plot.xaxis.axis_label = 'Wavelength [micron]' 

atm_plot.text([1.], [0.45], ['_________'], text_color='blue', text_font_style='bold') 
atm_plot.text([1.], [0.45], ['Combined'], text_color='blue', text_font_style='bold') 
atm_plot.text([1.], [0.41], ['Snow'], text_color='grey') 
atm_plot.text([1.], [0.38], ['Conifers'], text_color='green') 
atm_plot.text([1.], [0.35], ['Red Algae'], text_color='red') 
atm_plot.text([1.], [0.32], ['Ocean'], text_color='lightblue') 
 
atm_plot.line('w', 'f', source=full_spectrum, line_width=3, line_color='blue', line_alpha=1.0)
atm_plot.line('w', 'snow', source=full_spectrum, line_width=1, line_color='grey', line_alpha=1.0)
atm_plot.line('w', 'conifers', source=full_spectrum, line_width=1, line_color='green', line_alpha=1.0)
atm_plot.line('w', 'algae', source=full_spectrum, line_width=1, line_color='red', line_alpha=1.0)
atm_plot.line('w', 'ocean', source=full_spectrum, line_width=1, line_color='lightblue', line_alpha=1.0)

# Set up widgets
snow = Slider(title="Snow", value=0.1, start=0., end=1.0, step=0.1)
conifers = Slider(title="Conifers", value=0.2, start=0., end=1.0, step=0.1)
algae = Slider(title="Red Algae", value=0.1, start=0., end=1.0, step=0.1)
ocean = Slider(title="Ocean", value=0.6, start=0., end=1.0, step=0.1)

def update_data(attrname, old, new):

    print 'SNOW : ', snow.value 
    print 'CONIFERS : ', conifers.value 
    print 'OCEAN : ', ocean.value 

    ocean_scale = 1.0 - snow.value - conifers.value - algae.value 
    ocean.value = 1.0 - snow.value - conifers.value - algae.value 
 
    full_spectrum.data['f'] = snow.value * el['SNOW'][0] + conifers.value * el['CONIFERS'][0] + algae.value * el['ALGAE'][0] +  ocean_scale* el['OCEAN'][0]
    full_spectrum.data['snow'] = snow.value * el['SNOW'][0] 
    full_spectrum.data['conifers'] = conifers.value * el['CONIFERS'][0] 
    full_spectrum.data['algae'] = algae.value * el['ALGAE'][0] 
    full_spectrum.data['ocean'] = ocean_scale* el['OCEAN'][0] 

def update_on_callback(): 

    print 'SNOW : ', snow.value
    print 'CONIFERS : ', conifers.value
    print 'OCEAN : ', ocean.value

    ocean_scale = 1.0 - snow.value - conifers.value - algae.value
    ocean.value = 1.0 - snow.value - conifers.value - algae.value

    full_spectrum.data['f'] = snow.value * el['SNOW'][0] + conifers.value * el['CONIFERS'][0] + algae.value * el['ALGAE'][0] +  ocean_scale* el['OCEAN'][0]
    full_spectrum.data['snow'] = snow.value * el['SNOW'][0]
    full_spectrum.data['conifers'] = conifers.value * el['CONIFERS'][0]
    full_spectrum.data['algae'] = algae.value * el['ALGAE'][0]
    full_spectrum.data['ocean'] = ocean_scale* el['OCEAN'][0]

    

# iterate on changes to parameters 
#for w in [snow, conifers, algae, ocean]:
#    w.on_change('value', update_data)

# Set up layouts and add to document
inputs = Column(children=[snow, conifers, algae, ocean])
v = Row(children=[inputs, atm_plot])
curdoc().add_root(v)
curdoc().add_periodic_callback(update_on_callback,2000)



