import numpy as np
import matplotlib.image as mpimg

from bokeh.plotting import figure, gridplot, output_file, show
from bokeh.models import ColumnDataSource, HBox, VBoxForm, Paragraph, Range1d
from bokeh.io import hplot, vplot, curdoc
from bokeh.models.widgets import Select 

image1 = "http://www.stsci.edu/~tumlinso/HDST_source_z2.jpg" 
image2 = "HST_source_z2.jpg"

p1 = figure(x_range=[0, 10], y_range=[-10, 0], tools="pan,resize,save,box_zoom,wheel_zoom,reset",toolbar_location='above', \
			title='LUVOIR (12 m)')
p1.background_fill_color = "white"
p1.image_url(url=[image1], x=[0], y=[0], w=10, h=10)
p1.x_range = Range1d(0, 10, bounds=(0, 10))  
p1.y_range = Range1d(-10, 0, bounds=(-10,0))

p3 = figure(x_range=[0, 10], y_range=[-10, 0], tools="pan,resize,save,box_zoom,wheel_zoom,reset",toolbar_location='above', \
			title='Hubble')
p3.y_range = p1.y_range 
p3.x_range = p1.x_range 
p3.background_fill_color = "white"
p3.image_url(url=[image2], x=[0], y=[0.1], w=10, h=10)

p = gridplot([[p1, p3]]) 

curdoc().add_root(p)
