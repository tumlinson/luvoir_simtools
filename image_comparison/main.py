import numpy as np
import matplotlib.image as mpimg

from bokeh.plotting import figure, gridplot, output_file, show
from bokeh.models import ColumnDataSource, HBox, VBoxForm, HoverTool, Paragraph, Range1d
from bokeh.io import hplot, vplot, curdoc
from bokeh.models import HoverTool
from bokeh.models.widgets import Select 

image_to_use = Select(title="Image to See", value="Galaxy", options=["Galaxy (z=2)", "Deep Field", "Star Forming Region", "Perseus A", "Pluto"], width=200)

image1 = "http://www.stsci.edu/~tumlinso/HDST_source_z2.jpg" 
image2 = "http://www.stsci.edu/~tumlinso/HST_source_z2.jpg"

p1 = figure(x_range=[0, 10], y_range=[-10, 0], tools="pan,reset,resize,save,box_zoom,wheel_zoom",toolbar_location='above', \
			title='LUVOIR (12 m)')
p1.background_fill_color = "white"
p1.image_url(url=[image1], x=[0], y=[0], w=10, h=10)
p1.x_range = Range1d(0, 10, bounds=(0, 10))  
p1.y_range = Range1d(-10, 0, bounds=(-10,0))

p3 = figure(x_range=[0, 10], y_range=[-10, 0], tools="pan,reset,resize,save,box_zoom,wheel_zoom",toolbar_location='above', \
			title='Hubble')
p3.y_range = p1.y_range 
p3.x_range = p1.x_range 
p3.background_fill_color = "white"
p3.image_url(url=[image2], x=[0], y=[0.1], w=10, h=10)

def update_image(attr,old,new): 
  print new 
  if ('Gal' in new): 
      image1 = "http://www.stsci.edu/~tumlinso/HDST_source_z2.jpg" 
      image2 = "http://www.stsci.edu/~tumlinso/HST_source_z2.jpg"
  if ('Deep' in new): 
      image1 = "http://www.stsci.edu/~tumlinso/hdst16m_rgb_nosmoothing_3mas.jpg" 
      image2 = "http://www.stsci.edu/~tumlinso/hdst2.4m_rgb_smoothing_60mas_dimmed.jpg" 
  if ('Sta' in new): 
      image1 = "http://www.stsci.edu/~tumlinso/pretty.png" 
      image2 = "http://www.stsci.edu/~tumlinso/pretty_large.png" 
  if ('Pers' in new): 
      image1 = "http://www.stsci.edu/~tumlinso/ngc1275_large.png" 
      image2 = "http://www.stsci.edu/~tumlinso/ngc1275_small.png" 
  if ('Plu' in new): 
      image1 = "http://www.stsci.edu/~tumlinso/pluto_16m.jpg" 
      image2 = "http://www.stsci.edu/~tumlinso/pluto_2.4m.jpg" 
  p1.image_url(url=[image1], x=[0], y=[0], w=10, h=10)
  p3.image_url(url=[image2], x=[0], y=[0], w=10, h=10)



p = gridplot([[p1, p3]]) 

image_to_use.on_change('value', update_image)

curdoc().add_root(image_to_use)
curdoc().add_root(p)
