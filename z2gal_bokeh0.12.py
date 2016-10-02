
import numpy as np

from astropy.io import fits 

from bokeh.plotting import figure, gridplot, output_file, show
from bokeh.models import ColumnDataSource, HBox, VBoxForm, HoverTool, Paragraph, Range1d
from bokeh.io import hplot, vplot, curdoc
from bokeh.models import HoverTool

from bokeh.models.widgets import Slider

p1 = figure(x_range=[0, 10], y_range=[-10, 0], tools="pan,reset,resize,save,box_zoom,wheel_zoom",toolbar_location='above', \
			title='LUVOIR (12 m)')
p1.background_fill_color = "white"
p1.image_url(url=["http://www.stsci.edu/~tumlinso/HDST_source_z2.jpg"], x=[0], y=[0], w=10, h=10)
p1.x_range = Range1d(2, 8, bounds=(2, 8))  
p1.y_range = Range1d(-8.5, -2.5, bounds=(-8.5,-2.5))


p2 = figure(x_range=[0, 10], y_range=[-10, 0], tools="pan,reset,resize,save,box_zoom,wheel_zoom",toolbar_location='above', \
			title='JWST')
p2.y_range = p1.y_range 
p2.x_range = p1.x_range 
p2.background_fill_color = "white"
p2.image_url(url=["http://www.stsci.edu/~tumlinso/JWST_source_z2.jpg"], x=[0], y=[0], w=10, h=10)

p3 = figure(x_range=[0, 10], y_range=[-10, 0], tools="pan,reset,resize,save,box_zoom,wheel_zoom",toolbar_location='above', \
			title='Hubble')
p3.y_range = p1.y_range 
p3.x_range = p1.x_range 
p3.background_fill_color = "white"
p3.image_url(url=["http://www.stsci.edu/~tumlinso/HST_source_z2.jpg"], x=[0], y=[0.1], w=10, h=10)

p = gridplot([[p1, p2, p3]]) 


curdoc().add_root(p)



  
