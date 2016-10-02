''' Docstring 
'''
import numpy as np
import math 

from astropy.io import ascii 

from bokeh.io import output_file, gridplot 
from bokeh.plotting import Figure
from bokeh.resources import CDN
from bokeh.embed import components 
from bokeh.models import ColumnDataSource, HBox, VBoxForm, HoverTool, Paragraph, Range1d 
from bokeh.layouts import Column, Row, WidgetBox
from bokeh.models.widgets import Slider, TextInput, Select 
from bokeh.io import hplot, vplot, curdoc
from bokeh.embed import file_html
from bokeh.models.callbacks import CustomJS

import get_pysynphot_spectra

##### OLD NEW WAY TO GET TEMPLATE SPECTRA 
q = ascii.read('data/fos_qso_short.txt') 
sn = (1e-15*q['FLUX']*1. * (1.e15) * 36. ) ** 0.5 
junkf = 1e-15*q['FLUX'] 
junkf[q['WAVE'] < 1100.] = -999.  
junkf[q['WAVE'] > 1800.] = -999.  
old_spectrum = ColumnDataSource(data=dict(w=q['WAVE']*1., f=1e-15*q['FLUX']*1., w0=q['WAVE']*1., f0=1e-15*q['FLUX'], junkf=junkf, sn=sn)) 
spectrum_template = old_spectrum

##### START FOR NEW WAY TO GET TEMPLATE SPECTRA 
spec_dict = get_pysynphot_spectra.add_spectrum_to_library() 
template_to_start_with = 'QSO' 
spec_dict[template_to_start_with].wave 
spec_dict[template_to_start_with].flux # <---- these are the variables you need 
sn = (spec_dict[template_to_start_with].flux * 1.e15 * 36. ) ** 0.5
junkf = spec_dict[template_to_start_with].flux 
junkf[spec_dict[template_to_start_with].wave < 1100.] = -999.  
junkf[spec_dict[template_to_start_with].wave > 1800.] = -999.  
new_spectrum = ColumnDataSource(data=dict(w=spec_dict[template_to_start_with].wave, f=spec_dict[template_to_start_with].flux, \
                                   w0=spec_dict[template_to_start_with].wave, f0=spec_dict[template_to_start_with].flux, junkf=junkf, sn=sn)) 
spectrum_template = new_spectrum


flux_plot = Figure(plot_height=400, plot_width=800, 
              tools="crosshair,hover,pan,reset,resize,save,box_zoom,wheel_zoom", outline_line_color='black', 
              x_range=[900, 2000], y_range=[0, 4e-15], toolbar_location='above') 
flux_plot.x_range=Range1d(900,2000,bounds=(900,2000)) 
flux_plot.y_range=Range1d(0,4e-15,bounds=(0,None)) 
flux_plot.background_fill_color = "beige"
flux_plot.background_fill_alpha = 0.5 
flux_plot.yaxis.axis_label = 'Flux' 
flux_plot.xaxis.axis_label = 'Wavelength' 

flux_plot.line('w', 'f', source=spectrum_template, line_width=3, line_color='blue', line_alpha=0.3)

sn_plot = Figure(plot_height=400, plot_width=800, 
              tools="crosshair,hover,pan,reset,resize,save,box_zoom,wheel_zoom", outline_line_color='black', 
              x_range=[900, 2000], y_range=[0, 40], toolbar_location='above')
sn_plot.x_range=Range1d(900,2000,bounds=(900,2000)) 
sn_plot.y_range=Range1d(0,40,bounds=(0,None)) 
sn_plot.line('w', 'sn', source=spectrum_template, line_width=3, line_color='orange', line_alpha=0.6)
sn_plot.background_fill_color = "beige"
sn_plot.background_fill_alpha = 0.5 
sn_plot.xaxis.axis_label = 'Wavelength' 
sn_plot.yaxis.axis_label = 'S/N per resel' 

def update_data_old(attrname, old, new):
    print "INSIDE THE OLD CALLBACK FUNCTION" 
    spectrum_template.data['w'] = np.array(spectrum_template.data['w0']) * (1. + redshift.value)
    spectrum_template.data['f'] = np.array(spectrum_template.data['f0']) * 10.**( (18.-magnitude.value) / 2.5)
    sn = (np.array(spectrum_template.data['f']) * (1.e15) * 36. * (exptime.value / 1.) * (aperture.value / 12.) ) ** 0.5
    spectrum_template.data['sn'] = sn

    spectrum_template.data['junkf'] = (spectrum_template.data['f']) 
    spectrum_template.data['junkf'][np.where(np.array(spectrum_template.data['w']) < 1200.)] = -999.
    spectrum_template.data['junkf'][np.where(np.array(spectrum_template.data['w']) > 1700.)] = -999. 

def update_data_new(attrname, old, new): # use this one for updating pysynphot tempaltes 
   
    print "You have chosen template ", template.value, np.size(spec_dict[template.value].wave) 
    print spec_dict[template.value].flux  

    spectrum_template.data['w0'] = spec_dict[template.value].wave 
    spectrum_template.data['f0'] = spec_dict[template.value].flux 

    spectrum_template.data['w'] = np.array(spectrum_template.data['w0']) * (1. + redshift.value)
    spectrum_template.data['f'] = np.array(spectrum_template.data['f0']) * 10.**( (18.-magnitude.value) / 2.5)
    sn = (np.array(spectrum_template.data['f']) * (1.e15) * 36. * (exptime.value / 1.) * (aperture.value / 12.) ) ** 0.5
    spectrum_template.data['sn'] = sn
    spectrum_template.data['junkf'] = (spectrum_template.data['f']) 
    spectrum_template.data['junkf'][np.where(np.array(spectrum_template.data['w']) < 1200.)] = -999.
    spectrum_template.data['junkf'][np.where(np.array(spectrum_template.data['w']) > 1700.)] = -999. 

# fake source for managing callbacks 
source = ColumnDataSource(data=dict(value=[]))
source.on_change('data', update_data_new)

# Set up widgets and their callbacks (faking the mouseup policy via "source" b/c functional callback doesn't do that. 
template = Select(title="Template Spectrum", value="QSO", options=["QSO", "O5V Star", "G2V Star", "Orion Nebula", \
                            "Starburst, No Dust", "Starburst, E(B-V) = 0.6"])
redshift = Slider(title="Redshift", value=0.0, start=0., end=1.0, step=0.02, callback_policy='mouseup')
redshift.callback = CustomJS(args=dict(source=source), code="""
    source.data = { value: [cb_obj.value] }
""")
magnitude = Slider(title="Magnitude", value=18., start=15., end=20.0, step=0.1, callback_policy='mouseup')
magnitude.callback = CustomJS(args=dict(source=source), code="""
    source.data = { value: [cb_obj.value] }
""")

grating = Select(title="Grating", value="G130M", options=["G130M", "G160M"])
aperture= Slider(title="Aperture (meters)", value=12., start=2., end=20.0, step=1.0, callback_policy='mouseup')
aperture.callback = CustomJS(args=dict(source=source), code="""
    source.data = { value: [cb_obj.value] }
""")
exptime = Slider(title="exptime", value=1., start=1., end=10.0, step=0.1, callback_policy='mouseup')
exptime.callback = CustomJS(args=dict(source=source), code="""
    source.data = { value: [cb_obj.value] }
""")

# iterate on changes to parameters 
for w in [template, grating]:
    w.on_change('value', update_data_new)
 
# Set up layouts and add to document
inputs1 = Column(children=[template, redshift, magnitude])
inputs2 = Column(children=[grating, aperture, exptime])
b1 = Row(children=[inputs1, flux_plot])
b2 = Row(children=[inputs2, sn_plot])
v = Column(children=[b1, b2])
curdoc().add_root(v)
