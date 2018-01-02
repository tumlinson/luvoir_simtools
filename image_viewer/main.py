import dask.dataframe as dd
import holoviews as hv
import geoviews as gv
import param
from colorcet import cm
from bokeh.models import Slider, Button
from bokeh.layouts import layout
from bokeh.io import curdoc
from bokeh.models import WMTSTileSource, Range1d
from bokeh.models.widgets import Select 

from holoviews.operation.datashader import datashade, aggregate, shade
from holoviews.plotting.util import fire

import set_plot_options as sp 

shade.cmap = fire

hv.extension('bokeh')
renderer = hv.renderer('bokeh').instance(mode='server')

ddf = dd.read_parquet('/Users/tumlinson/Dropbox/jupytercon2017-holoviews-tutorial/data/nyc_taxi_short_hours.parq/').persist() 
panel1_url = 'http://jt-astro.science/PHATZoom/phat_0pix_padded/{Z}/{X}/{Y}.png'
panel2_url =    'http://jt-astro.science/PHATZoom/phat_5pix_padded/{Z}/{X}/{Y}.png'
panel1 = gv.WMTS(WMTSTileSource(url=panel1_url)) 
panel2 = gv.WMTS(WMTSTileSource(url=panel2_url)) 

stream = hv.streams.Stream.define('HourSelect', hour=0)()
points = hv.Points(ddf, kdims=['dropoff_x', 'dropoff_y'])
dmap = hv.util.Dynamic(points, operation=lambda obj, hour: obj.select(dropoff_hour=hour),streams=[stream]) 
                       
# Apply aggregation
aggregated = aggregate(dmap, link_inputs=True, streams=[hv.streams.RangeXY], width=400, height=400)
shaded = shade(aggregated, link_inputs=True) 

# Define PointerX stream, attach to points and declare DynamicMap for cross-section and VLine
pointer = hv.streams.PointerX(x=ddf.dropoff_x.loc[0].compute().iloc[0], source=points)
section = hv.util.Dynamic(aggregated, operation=lambda obj, x: obj.sample(dropoff_x=x),
                          streams=[pointer], link_inputs=False).relabel('')
vline = hv.DynamicMap(lambda x: hv.VLine(x), streams=[pointer])

# Define options
hv.opts("RGB [width=800 height=400 xaxis=None yaxis=None fontsize={'title': '14pt'}] VLine (color='white' line_width=2)")
hv.opts("Curve [width=150 yaxis=None show_frame=False] (color='black') {+framewise}") 

hvobj = (panel1 * shaded) + (panel2 * shaded) 

plot = renderer.get_plot(hvobj, doc=curdoc())### Pass the HoloViews object to the renderer
#plot.handles is a dictionary, plot.state is a Column, plot.handles['plots'] is a list, 
#plot.handles['plots'][0] is the top row, plot.handles['plots'][1] is the bottom row 

upper_left = plot.handles['plots'][0][0]    # Figure class 
upper_right = plot.handles['plots'][0][1]    # Figure class 

upper_left.x_range=Range1d(-2e7,2e7,bounds=(-3e7,3e7))
upper_left.y_range=Range1d(-2e7,2e7,bounds=(-3e7,3e7))
upper_right.x_range = upper_left.x_range
upper_right.y_range = upper_left.y_range

upper_left.title.text = 'Full LUVOIR Resolution' 
upper_right.title.text = 'Blurred and Binned' 

sp.set_plot_options(upper_left) # plot.state has bokeh type Figure, so can be manipulated in the usual way 
sp.set_plot_options(upper_right) # plot.state has bokeh type Figure, so can be manipulated in the usual way 

#image_to_use = Select(title="Image to See", value="Galaxy", options=["Galaxy (z=2)", "Deep Field", "Star Forming Region", "Perseus A", "Pluto"], width=200)

#def update_image(attr,old,new): 
#  if ('PHAT' in new): 
#      panel1_url = 'http://jt-astro.science/PHATZoom/phat_0pix_padded/{Z}/{X}/{Y}.png'
#      panel2_url = 'http://jt-astro.science/PHATZoom/phat_5pix_padded/{Z}/{X}/{Y}.png'
#  if ('Deep' in new): 
#      panel1_url = "http://www.stsci.edu/~tumlinso/hdst16m_rgb_nosmoothing_3mas.jpg" 
#      panel2_url = "http://www.stsci.edu/~tumlinso/hdst2.4m_rgb_smoothing_60mas_dimmed.jpg" 
#  if ('Sta' in new): 
#      panel1_url = "http://www.stsci.edu/~tumlinso/pretty.png" 
#      panel2_url = "http://www.stsci.edu/~tumlinso/pretty_large.png" 
#  if ('Pers' in new): 
#      panel1_url = "http://www.stsci.edu/~tumlinso/ngc1275_large.png" 
#      panel2_url = "http://www.stsci.edu/~tumlinso/ngc1275_small.png" 
#  if ('Plu' in new): 
#      panel1_url = "http://www.stsci.edu/~tumlinso/pluto_16m.jpg" 
#      panel2_url = "http://www.stsci.edu/~tumlinso/pluto_2.4m.jpg" 
#  panel1 = gv.WMTS(WMTSTileSource(url=panel1_url))
#  panel2 = gv.WMTS(WMTSTileSource(url=panel2_url))
#  hvobj = (panel1 * shaded) + (panel2 * shaded) 
#  print(panel1_url, panel2_url) 
#
#image_to_use.on_change('value', update_image)

# Combine the bokeh plot on plot.state with the widgets
l = layout(plot.state, sizing_mode='fixed')
curdoc().add_root(l)
#curdoc().add_root(image_to_use)


