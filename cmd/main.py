### based on /Users/tumlinson/jupytercon2017-holoviews-tutorial/notebooks/apps/player_app.py 
import holoviews as hv
import parambokeh
import param
import numpy as np 
from colorcet import cm
from bokeh.layouts import layout
from bokeh.io import curdoc
from bokeh.models import ColumnDataSource, Range1d, Slider, Panel, Tabs, Column, Div 
from holoviews.operation.datashader import datashade
import astropy.units as u 

from syotools.models import Camera, Telescope, Spectrograph, PhotometricExposure, SpectrographicExposure

import load_dataset as l 
import set_plot_options as sp 
import cmd_help as h

hv.extension('bokeh')
renderer = hv.renderer('bokeh').instance(mode='server')

cmd_frame = l.load_datasets() # this is the CMD dataset 
cmd_points = hv.Points(cmd_frame, kdims=['grcolor', 'rmag']) # this is the inital creation of the HV "Points" object that will be shaded 


def select_stars(obj, age, mass, phase):               # received "obj" of type "Points" and "age" of type ordinary float 
    print("we now have age / mass inside select_stars", age, mass, phase) 
    #print(obj.select(logage=age).dframe())  
    return obj.select(ageindex=age) # this returns "Points", so could be anything here that munges it 

# shading and streaming is here 
age_stream = hv.streams.Stream.define('AgeSelect', age=80)()
mass_stream = hv.streams.Stream.define('MassSelect', mass=1.)()
phase_stream = hv.streams.Stream.define('StageSelect', phase=0.)()
dmap = hv.util.Dynamic(cmd_points, operation=select_stars,    # select_stars is the function that will take cmd_points and munge it 
           streams=[age_stream, mass_stream, phase_stream])   # unsurprisingly, dmap has type "Dynamic Map" 

# set up the colormap picker 
class ColormapPicker(hv.streams.Stream):
    colormap   = param.ObjectSelector(default=cm["bgy"], # sets the default colormap to "blues" 
                                      objects=[cm[k] for k in cm.keys() if not '_' in k])

cmap_picker = ColormapPicker(rename={'colormap': 'cmap'}, name='')
widget = parambokeh.Widgets(cmap_picker, mode='raw') # the color picker 

shaded = datashade(dmap, streams=[hv.streams.RangeXY, cmap_picker], y_range=(-13,7), y_sampling=0.05, x_sampling=0.025, height=1000) # "sampling" parameters control "pixel size" 
hv.opts("RGB [width=400 height=800 xaxis=bottom yaxis=left fontsize={'title': '14pt'}]")
hv.opts("Curve [width=150 yaxis=None show_frame=False] (color='black') {+framewise} Layout [shared_axes=False]")
hv.opts("Points [tools=['box_select']]")

plot = renderer.get_plot(shaded, doc=curdoc())     ### Pass the HoloViews object to the renderer



###########################################
# CREATE THE SYOTOOLS ELEMENTS AND MODELS # 
###########################################
e, c, t = PhotometricExposure(), Camera(), Telescope()
t.add_camera(c)
t.aperture = 15.0 * u.meter 
c.add_exposure(e)
e.unknown = 'magnitude'

print("\n\n==Setting spectrum to Flat AB & calculating==\n")
e.sed_id = 'fab'
e.snr = 5. * (u.electron**0.5) 
e.exptime = 3600. * u.s 
print("\n\n==Setting unknown to 'magnitude'==\n")
print("\nInput Exptime: {}".format(e.exptime))
print("\nInput SNR: {}".format(e.snr))
print("\nOutput Magnitude: {}".format(e.magnitude))

###########################################
# DONE WITH SYOTOOLS ELEMENTS AND MODELS # 
###########################################

# results of ETC are stored weirdly the list of AB mags =  e.magnitude[1]['value'][:] 
etc_label_source = ColumnDataSource(data={'mags': map(lambda n: '%.2f'%n, e.magnitude[1]['value'][:]), 
					'x': map(lambda n: 2., e.magnitude[1]['value'][:]), 
					'y': [-5*(i-2)-0.4 for i in range(5)]}) 
plot.state.text('x','y','mags', source=etc_label_source, text_font_size='15pt', text_color='red', text_align='right')

mag_label_source = ColumnDataSource(data={'x': [3.0,3.0,3.0,3.0,3.0],
                        'y': [-10-0.4,-5-0.4,0-0.4,5-0.4,10-0.4], 'text':['35.0','30.0','25.0','20.0','15.0']}) 
plot.state.text('x','y','text', source=mag_label_source, text_font_size='12pt', text_color='deepskyblue', text_align='right')


def actual_age_slider_update(attrname, old, new):             
    # this is necessary because the table of values often have non-exact age values, e.g. 9.45000001 
    age_slider_dict = {'9.1':72,'9.15':73, '9.2':74, '9.25':75, '6':10, '7':30,'8':50,'9':70,'10':90} 
    age_list = np.arange(94) * 0.05 + 5.5
    for entry, integer in zip(age_list, np.arange(94)): 
        age_slider_dict[str(entry)] = integer 
    age_stream.event(age=age_slider_dict[str(new)]) 

def distance_slider_update(attrname, old, new):             
    distmod = 5. * np.log10((new+1e-5) * 1e6) - 5. 
    mag_label_source.data['text'] = (distmod+np.array([10,5,0,-5,-10])).astype('|S5')

def mass_slider_update(attrname, old, new):             
    mass_stream.event(mass=new)

def phase_slider_update(attrname, old, new):             
    phase_stream.event(phase=new)

def exposure_update(attrname, old, new):             
    print("calling updater with aperture = ", aperture_slider.value, '   and exptime = ', exptime_slider.value) 
    t.aperture = aperture_slider.value * u.meter 
    e.exptime = exptime_slider.value * 3600. * u.s 
    e.unknown = 'magnitude' 
    etc_label_source.data = {'mags': map(lambda n: '%.2f'%n, e.magnitude[1]['value'][:]), 
					'x': map(lambda n: 2., e.magnitude[1]['value'][:]),
					'y': [-5*(i-2)-0.4 for i in range(5)]}  


astro_controls = [] 
exposure_controls = [] 
visual_controls = [widget] 

actual_age_slider = Slider(start=5.5, end=10.15, value=10., step=0.05, title="Log(Age in Gyr)")
actual_age_slider.on_change('value', actual_age_slider_update)
astro_controls.append(actual_age_slider) 

distance_slider = Slider(start=0.0, end=20., value=1., step=0.5, title="Distance [Mpc]")
distance_slider.on_change('value', distance_slider_update)
astro_controls.append(distance_slider) 

mass_slider = Slider(start=0.1, end=10., value=1., step=0.05, title="Mass")
mass_slider.on_change('value', mass_slider_update)
#astro_controls.append(mass_slider) 

phase_slider = Slider(start=0, end=5, value=0, step=1, title="Evolutionary Stage")
phase_slider.on_change('value', phase_slider_update)
#astro_controls.append(phase_slider) 

aperture_slider = Slider(start=1, end=20, value=15, step=1, title="Aperture [meters]")
aperture_slider.on_change('value', exposure_update)
exposure_controls.append(aperture_slider) 

exptime_slider = Slider(title="Exptime [hours]", value=1., start=0.1, end=50.0, step=0.1, callback_policy='mouseup')
exptime_slider.on_change('value', exposure_update)
exposure_controls.append(exptime_slider) 



sp.set_plot_options(plot.state) # plot.state has type Figure from bokeh, so can be manipulated in the usual way 

astro_tab = Panel(child=Column(children=astro_controls), title='Stars') 
exposure_tab = Panel(child=Column(children=exposure_controls), title='Exposure') 
info_tab = Panel(child=Div(text = h.help(), width=300), title='Info') 
visual_tab = Panel(child=Column(children=[widget]), title='Visuals') 
controls = Tabs(tabs=[astro_tab, exposure_tab, visual_tab, info_tab], width=400)

layout = layout([[controls, plot.state]], sizing_mode='fixed')
curdoc().add_root(layout)




