### based on /Users/tumlinson/jupytercon2017-holoviews-tutorial/notebooks/apps/player_app.py 
import holoviews as hv
import parambokeh
import param
from colorcet import cm
from bokeh.layouts import layout
from bokeh.io import curdoc
from bokeh.models import ColumnDataSource, Range1d, Slider
from holoviews.operation.datashader import datashade

import load_dataset as l 
import set_plot_options as sp 

hv.extension('bokeh')
renderer = hv.renderer('bokeh').instance(mode='server')

cmd_frame = l.load_datasets() # this is the CMD dataset 
cmd_points = hv.Points(cmd_frame, kdims=['dropoff_x', 'dropoff_y']) # 

def select_stars(obj, age, mass, stage):               # received "obj" of type "Points" and "age" of type ordinary float 
    print("we now have age / mass inside select_stars", age, mass, stage) 
    return obj.select(dropoff_age=age) # this returns "points", so could be anything here that munges it 

# shading and streaming is here 
age_stream = hv.streams.Stream.define('AgeSelect', age=6.)()
mass_stream = hv.streams.Stream.define('MassSelect', mass=1.)()
stage_stream = hv.streams.Stream.define('StageSelect', stage=1)()
dmap = hv.util.Dynamic(cmd_points, operation=select_stars, # select_stars is the function that will take cmd_points and munge it 
           streams=[age_stream, mass_stream, stage_stream]) # unsurprisingly, dmap has type "Dynamic Map" 

# set up the colormap picker 
class ColormapPicker(hv.streams.Stream):
    colormap   = param.ObjectSelector(default=cm["bgy"], # sets the default colormap to "blues" 
                                      objects=[cm[k] for k in cm.keys() if not '_' in k])

cmap_picker = ColormapPicker(rename={'colormap': 'cmap'}, name='')
widget = parambokeh.Widgets(cmap_picker, mode='raw') # the color picker 

shaded = datashade(dmap, streams=[hv.streams.RangeXY, cmap_picker], y_range=(-13,7), y_sampling=0.2, x_sampling=0.1, height=1000) # "sampling" parameters control "pixel size" 
hv.opts("RGB [width=400 height=800 xaxis=bottom yaxis=left fontsize={'title': '14pt'}]")
hv.opts("Curve [width=150 yaxis=None show_frame=False] (color='black') {+framewise} Layout [shared_axes=False]")

plot = renderer.get_plot(shaded, doc=curdoc())     ### Pass the HoloViews object to the renderer

def age_slider_update(attrname, old, new):             
    age_stream.event(age=new)

def mass_slider_update(attrname, old, new):             
    mass_stream.event(mass=new)

def stage_slider_update(attrname, old, new):             
    stage_stream.event(stage=new)

age_slider = Slider(start=5.5, end=10., value=6., step=0.05, title="Age")
age_slider.on_change('value', age_slider_update)

mass_slider = Slider(start=0.1, end=10., value=1., step=0.05, title="Mass")
mass_slider.on_change('value', mass_slider_update)

stage_slider = Slider(start=1, end=5, value=1, step=1, title="Evolutionary Stage")
stage_slider.on_change('value', stage_slider_update)

sp.set_plot_options(plot.state) # plot.state has type Figure from bokeh, so can be manipulated in the usual way 

layout = layout([[[widget, age_slider, mass_slider, stage_slider], plot.state], ], sizing_mode='fixed')

curdoc().add_root(layout)
