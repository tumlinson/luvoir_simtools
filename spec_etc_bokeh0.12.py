''' Docstring 
'''
import numpy as np

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

import Telescope as T 

luvoir = T.Telescope(10., 280., 500.) # set up LUVOIR with 10 meters, T = 280, and diff limit at 500 nm 

def simulate_exposure(telescope, flux, exptime): 
    print "Attempting to create an exposure for Telescope: ", telescope.name, telescope.aperture, ' m' 
    sn = ( np.array(flux) * (1.e16) * 100. * (exptime / 0.1) * (telescope.aperture / 12.)**2 ) ** 0.5
    return sn

##### START FOR NEW WAY TO GET TEMPLATE SPECTRA 
spec_dict = get_pysynphot_spectra.add_spectrum_to_library() 
template_to_start_with = 'QSO' 
spec_dict[template_to_start_with].wave 
spec_dict[template_to_start_with].flux # <---- these are the variables you need 

# THIS IS THE ENTIRE S/N CALCULATION 
#sn = (spec_dict[template_to_start_with].flux * 1.e16 * 100. ) ** 0.5
signal_to_noise = simulate_exposure(luvoir, spec_dict[template_to_start_with].flux, 0.1) 

flux_cut = spec_dict[template_to_start_with].flux 
flux_cut[spec_dict[template_to_start_with].wave < 1100.] = -999.  
flux_cut[spec_dict[template_to_start_with].wave > 1800.] = -999.  
spectrum_template = ColumnDataSource(data=dict(w=spec_dict[template_to_start_with].wave, f=spec_dict[template_to_start_with].flux, \
                                   w0=spec_dict[template_to_start_with].wave, f0=spec_dict[template_to_start_with].flux, \
                                   flux_cut=flux_cut, sn=signal_to_noise)) 

# set up the flux plot 
flux_plot = Figure(plot_height=400, plot_width=800, 
              tools="crosshair,hover,pan,reset,resize,save,box_zoom,wheel_zoom", outline_line_color='black', 
              x_range=[900, 2000], y_range=[0, 4e-16], toolbar_location='above') 
flux_plot.x_range=Range1d(900,2000,bounds=(900,2000)) 
flux_plot.y_range=Range1d(0,4e-16,bounds=(0,None)) 
flux_plot.background_fill_color = "beige"
flux_plot.background_fill_alpha = 0.5 
flux_plot.yaxis.axis_label = 'Flux' 
flux_plot.xaxis.axis_label = 'Wavelength' 
flux_plot.line('w', 'f', source=spectrum_template, line_width=3, line_color='blue', line_alpha=0.3)

# set up the flux plot 
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

def update_data(attrname, old, new): # use this one for updating pysynphot tempaltes 
   
    print "You have chosen template ", template.value, np.size(spec_dict[template.value].wave) 

    spectrum_template.data['w0'] = spec_dict[template.value].wave 
    spectrum_template.data['f0'] = spec_dict[template.value].flux 

    spectrum_template.data['w'] = np.array(spectrum_template.data['w0']) * (1. + redshift.value)
    spectrum_template.data['f'] = np.array(spectrum_template.data['f0']) * 10.**( (21.-magnitude.value) / 2.5)

    # THIS IS THE ENTIRE S/N CALCULATION 
    luvoir.aperture = aperture.value 
    #sn = (np.array(spectrum_template.data['f']) * (1.e16) * 100. * (exptime.value / 0.1) * (aperture.value / 12.) ) ** 0.5
    signal_to_noise = simulate_exposure(luvoir, spectrum_template.data['f'], exptime.value) 

    spectrum_template.data['sn'] = signal_to_noise 
    spectrum_template.data['flux_cut'] = (spectrum_template.data['f']) 
    spectrum_template.data['flux_cut'][np.where(np.array(spectrum_template.data['w']) < 1200.)] = -999.
    spectrum_template.data['flux_cut'][np.where(np.array(spectrum_template.data['w']) > 1700.)] = -999. 

# fake source for managing callbacks 
source = ColumnDataSource(data=dict(value=[]))
source.on_change('data', update_data)

# Set up widgets and their callbacks (faking the mouseup policy via "source" b/c functional callback doesn't do that. 
template = Select(title="Template Spectrum", value="QSO", options=["QSO", "O5V Star", "G2V Star", "Orion Nebula", \
                            "Starburst, No Dust", "Starburst, E(B-V) = 0.6"])
redshift = Slider(title="Redshift", value=0.0, start=0., end=1.0, step=0.02, callback_policy='mouseup')
redshift.callback = CustomJS(args=dict(source=source), code="""
    source.data = { value: [cb_obj.value] }
""")
magnitude = Slider(title="Magnitude", value=21., start=15., end=25.0, step=0.1, callback_policy='mouseup')
magnitude.callback = CustomJS(args=dict(source=source), code="""
    source.data = { value: [cb_obj.value] }
""")
grating = Select(title="Grating", value="G130M", options=["G130M", "G160M"])
aperture= Slider(title="Aperture (meters)", value=12., start=2., end=20.0, step=1.0, callback_policy='mouseup')
aperture.callback = CustomJS(args=dict(source=source), code="""
    source.data = { value: [cb_obj.value] }
""")
exptime = Slider(title="exptime", value=0.1, start=0.1, end=10.0, step=0.1, callback_policy='mouseup')
exptime.callback = CustomJS(args=dict(source=source), code="""
    source.data = { value: [cb_obj.value] }
""")

# iterate on changes to parameters 
for w in [template, grating]:  w.on_change('value', update_data)
 
# Set up layouts and add to document
source_inputs = Column(children=[template, redshift, magnitude])
exposure_inputs = Column(children=[grating, aperture, exptime])
row1 = Row(children=[source_inputs, flux_plot])
row2 = Row(children=[exposure_inputs, sn_plot])
curdoc().add_root(Column(children=[row1, row2]))

