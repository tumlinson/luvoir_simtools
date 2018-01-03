import dask.dataframe as dd
import holoviews as hv
import geoviews as gv
import param
from colorcet import cm
from bokeh.models import Slider, Button
from bokeh.layouts import layout
from bokeh.io import curdoc
from bokeh.models import WMTSTileSource, Range1d

from holoviews.operation.datashader import datashade, aggregate, shade
from holoviews.plotting.util import fire

import foggie_plot_options as sp 

shade.cmap = fire

hv.extension('bokeh')
renderer = hv.renderer('bokeh').instance(mode='server')

ddf = dd.read_parquet('/Users/tumlinson/Dropbox/jupytercon2017-holoviews-tutorial/data/nyc_taxi_short_hours.parq/').persist() 
#density_url = 'http://jt-astro.science/CGM_bigbox_tile/density_tiles/{Z}/{X}/{Y}.png'
density_url = 'http://jt-astro.science/halo_008508_tile/density_tiles/{Z}/{X}/{Y}.png'
temp_url = 'http://jt-astro.science/CGM_bigbox_tile/temperature_tiles/{Z}/{X}/{Y}.png'
metallicity_url = 'http://jt-astro.science/CGM_bigbox_tile/metallicity_tiles/{Z}/{X}/{Y}.png'
HI_density_url = 'http://jt-astro.science/CGM_bigbox_tile/HI_Density_tiles/{Z}/{X}/{Y}.png'
density = gv.WMTS(WMTSTileSource(url=density_url)) 
temperature = gv.WMTS(WMTSTileSource(url=temp_url)) 
metallicity = gv.WMTS(WMTSTileSource(url=metallicity_url)) 
HI_density = gv.WMTS(WMTSTileSource(url=HI_density_url)) 

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
hv.opts("RGB [width=500 height=500 xaxis=None yaxis=None fontsize={'title': '14pt'}] VLine (color='white' line_width=2)")
hv.opts("Curve [width=150 yaxis=None show_frame=False] (color='black') {+framewise}") 

hvobj = ((density * shaded) + (temperature * shaded) + (metallicity * shaded) + (HI_density * shaded))# Combine it all into a complex "layout" object  

### Pass the HoloViews object to the renderer
plot = renderer.get_plot(hvobj.cols(2), doc=curdoc())
#plot.handles is a dictionary 
#plot.state is a Column 
#plot.handles['plots'] is a list 
#plot.handles['plots'][0] is the top row 
#plot.handles['plots'][1] is the bottom row 

upper_left = plot.handles['plots'][0][0]    # Figure class 
upper_right = plot.handles['plots'][0][1]    # Figure class 
lower_left = plot.handles['plots'][1][0]    # Figure class 
lower_right = plot.handles['plots'][1][1]    # Figure class 

upper_left.x_range=Range1d(-2e7,2e7,bounds=(-3e7,3e7))
upper_left.y_range=Range1d(-2e7,2e7,bounds=(-3e7,3e7))
upper_right.x_range = upper_left.x_range
upper_right.y_range = upper_left.y_range
lower_left.x_range = upper_left.x_range
lower_left.y_range = upper_left.y_range
lower_right.x_range = upper_left.x_range
lower_right.y_range = upper_left.y_range

upper_left.title.text = 'Density' 
upper_right.title.text = 'Temperature' 
lower_left.title.text = 'Metallicity' 
lower_right.title.text = 'HI Density' 

sp.set_plot_options(upper_left) # plot.state has bokeh type Figure, so can be manipulated in the usual way 
sp.set_plot_options(upper_right) # plot.state has bokeh type Figure, so can be manipulated in the usual way 
sp.set_plot_options(lower_left) # plot.state has bokeh type Figure, so can be manipulated in the usual way 
sp.set_plot_options(lower_right) # plot.state has bokeh type Figure, so can be manipulated in the usual way 

# Combine the bokeh plot on plot.state with the widgets
l = layout(plot.state, sizing_mode='fixed')
curdoc().add_root(l)


