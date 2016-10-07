
''' A dead simple ETC for HDST 
'''
import numpy as np
from bokeh.io import output_file, gridplot 

import phot_compute_snr as phot_etc 

from bokeh.plotting import Figure
from bokeh.resources import CDN
from bokeh.embed import components, autoload_server 
from bokeh.models import ColumnDataSource, HBox, VBoxForm, HoverTool, Paragraph, Range1d 
from bokeh.layouts import column, row, WidgetBox 
from bokeh.models.widgets import Slider
from bokeh.io import hplot, vplot, curdoc
from bokeh.embed import file_html

import Telescope as T 

luvoir = T.Telescope(10., 280., 500.) # set up LUVOIR with 10 meters, T = 280, and diff limit at 500 nm 
hdi = T.Camera()                     # and HDI camera with default bandpasses 
hdi.set_pixel_sizes(luvoir) 

# set up ColumnDataSources for main SNR plot 
snr = phot_etc.compute_snr(luvoir, hdi, 1., 32.)
source = ColumnDataSource(data=dict(x=hdi.pivotwave[2:-3], y=snr[2:-3], desc=hdi.bandnames[2:-3] ))
source2 = ColumnDataSource(data=dict(x=hdi.pivotwave[0:2], y=snr[0:2], desc=hdi.bandnames[0:2]))
source3 = ColumnDataSource(data=dict(x=hdi.pivotwave[-3:], y=snr[-3:], desc=hdi.bandnames[-3:]))

hover = HoverTool(point_policy="snap_to_data", 
        tooltips="""
        <div>
            <div>
                <span style="font-size: 17px; font-weight: bold; color: #696">@desc band</span>
            </div>
            <div>
                <span style="font-size: 15px; font-weight: bold; color: #696">S/N = </span>
                <span style="font-size: 15px; font-weight: bold; color: #696;">@y</span>
            </div>
        </div>
        """
    )


# Set up plot
snr_plot = Figure(plot_height=400, plot_width=800, 
              tools="crosshair,pan,reset,resize,save,box_zoom,wheel_zoom",
              x_range=[120, 2300], y_range=[0, 40], toolbar_location='right')
snr_plot.x_range = Range1d(120, 2300, bounds=(120, 2300)) 
snr_plot.add_tools(hover)
snr_plot.background_fill_color = "beige"
snr_plot.background_fill_alpha = 0.5
snr_plot.yaxis.axis_label = 'SNR'
snr_plot.xaxis.axis_label = 'Wavelength (nm)'
snr_plot.text(5500, 20, text=['V'], text_align='center', text_color='red')

snr_plot.line('x', 'y', source=source, line_width=3, line_alpha=1.0) 
snr_plot.circle('x', 'y', source=source, fill_color='white', line_color='blue', size=10)
    
snr_plot.line('x', 'y', source=source2, line_width=3, line_color='orange', line_alpha=1.0)
snr_plot.circle('x', 'y', source=source2, fill_color='white', line_color='orange', size=8) 
    
snr_plot.line('x', 'y', source=source3, line_width=3, line_color='red', line_alpha=1.0)
snr_plot.circle('x', 'y', source=source3, fill_color='white', line_color='red', size=8) 

# Set up widgets
aperture= Slider(title="Aperture (meters)", value=12., start=2., end=20.0, step=1.0)
exptime = Slider(title="Exptime (hours)", value=1., start=0., end=10.0, step=0.1)
magnitude = Slider(title="Magnitude (AB)", value=32.0, start=10.0, end=35.)

def update_data(attrname, old, new):

    #a = aperture.value 
    m = magnitude.value
    e = exptime.value

    luvoir.aperture = aperture.value 
    hdi.set_pixel_sizes(luvoir) # adaptively set the pixel sizes 

    wave = hdi.pivotwave 
    snr = phot_etc.compute_snr(luvoir, hdi, e, m) 
    source.data = dict(x=wave[2:-3], y=snr[2:-3], desc=hdi.bandnames[2:-3]) 
    source2.data = dict(x=hdi.pivotwave[0:2], y=snr[0:2], desc=hdi.bandnames[0:2]) 
    source3.data = dict(x=hdi.pivotwave[-3:], y=snr[-3:], desc=hdi.bandnames[-3:]) 


for w in [aperture, exptime, magnitude]: # iterate on changes to parameters 
    w.on_change('value', update_data)

# Set up layouts and add to document
inputs = WidgetBox(children=[aperture, exptime, magnitude]) 
curdoc().add_root(row(children=[inputs, snr_plot])) 
script = autoload_server(model=None, app_path="/simple_etc", url="pancho.local:5006")
#print(script)
