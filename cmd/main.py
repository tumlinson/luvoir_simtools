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
import os 
import pandas as pd 
from bokeh.models.callbacks import CustomJS

from syotools.models import Camera, Telescope, Spectrograph, PhotometricExposure, SpectrographicExposure

import load_dataset as l 
import cmd_plot_options as sp 
import cmd_help as h
import get_crowding_limit as crowd

cwd = os.getenv('LUVOIR_SIMTOOLS_DIR')

pars = curdoc().session_context.request.arguments # how to get paramters in off the URL 

hv.extension('bokeh')
renderer = hv.renderer('bokeh').instance(mode='server')


#cmd_frame = l.load_datasets()                                # this is the CMD dataset, returned from load_datasets as a pandas dataframe 
#cmd_frame.to_pickle('cmd/cmd_frame_large_no_noise.pkl') 
cmd_frame = pd.read_pickle(cwd+'data/cmd_frame_large.pkl') # this one has noise in it 
cmd_frame = pd.read_pickle(cwd+'data/cmd_frame_large_no_noise.pkl') 

cmd_points = hv.Points(cmd_frame, kdims=['grcolor', 'rmag']) # this is the inital creation of the HV "Points" object that will be shaded 
							     # by default this will shade all ages and metallicities 


def add_noise(new_frame, noise_scale): 
    noise_basis = 10. / 10.**((30.-(-1.*new_frame.rmag)) / 2.5 / 2.) # mind the 10! 
    r_noise = np.random.normal(0.0, noise_scale, np.size(new_frame.rmag)) * noise_basis 
    g_noise = np.random.normal(0.0, noise_scale, np.size(new_frame.rmag)) * noise_basis 
    new_frame.rmag = new_frame.rmag + r_noise 
    new_frame.gmag = new_frame.gmag + g_noise 
    new_frame.grcolor = -1. * (new_frame.gmag - new_frame.rmag) 
    new_frame.grcolor[new_frame.grcolor > 4.2] = 4.2
    new_frame.grcolor[new_frame.grcolor < -1.2] = -1.2 
    return new_frame 

def select_stars(obj, age, metallicity, noise):               # received "obj" of type "Points" and "age" of type ordinary float 
    #"obj" incoming is the points object 
    print("age / metallicity / noise inside select_stars", age, metallicity, noise) 
    new_frame = cmd_frame.loc[lambda cmd_frame: (cmd_frame.metalindex == metallicity) & (cmd_frame.ageindex == age)]
    noise_frame = add_noise(new_frame, 1.0 * noise) 
    noise_frame.to_pickle('noise_frame.pkl') 
    cmd_points = hv.Points(noise_frame, kdims=['grcolor', 'rmag']) 
    return cmd_points 

age_stream = hv.streams.Stream.define('AgeSelect', age=80)()
metallicity_stream = hv.streams.Stream.define('MetallicitySelect', metallicity=0)()
noise_stream = hv.streams.Stream.define('NoiseScale', noise=0)() 			# will be used to scale noise 
dmap = hv.util.Dynamic(cmd_points, operation=select_stars,    # select_stars is the function that will take cmd_points and munge it 
           streams=[age_stream, metallicity_stream, noise_stream])   # unsurprisingly, dmap has type "Dynamic Map" 

class ColormapPicker(hv.streams.Stream):                      # set up the colormap picker 
    colormap=param.ObjectSelector(default=cm["kbc"],objects=[cm[k] for k in cm.keys() if not '_' in k])

cmap_picker = ColormapPicker(rename={'colormap': 'cmap'}, name='')
widget = parambokeh.Widgets(cmap_picker, mode='raw') # the color picker 

shaded=datashade(dmap, streams=[hv.streams.RangeXY,cmap_picker],y_range=(-13,7), 
                 y_sampling=0.10,x_sampling=0.050,height=1000) # "sampling" parameters control "pixel size" 
hv.opts("RGB [width=400 height=800 xaxis=bottom yaxis=left fontsize={'title': '14pt'}]")
hv.opts("Points [tools=['box_select']]")

plot = renderer.get_plot(shaded, doc=curdoc())     ### Pass the HoloViews object to the renderer

plot.state.quad(top=[-10.5], bottom=[-9.8], left=[2.7], right=[3.9], fill_color='white', fill_alpha=0.8, line_alpha=0.) 
plot.state.quad(top=[-5.5], bottom=[-4.8], left=[2.7], right=[3.9], fill_color='white', fill_alpha=0.8, line_alpha=0.) 
plot.state.quad(top=[-0.5], bottom=[0.8], left=[2.7], right=[3.9], fill_color='white', fill_alpha=0.8, line_alpha=0.) 
plot.state.quad(top=[4.5], bottom=[5.8], left=[2.7], right=[3.9], fill_color='white', fill_alpha=0.8, line_alpha=0.) 

mag_label_source = ColumnDataSource(data={'x': [3.8,3.8,3.8,3.8,3.8], # a data source for the apparent magnitudes displayed on the plot 
                        'y': [-10-0.4,-5-0.4,0-0.4,5-0.4,10-0.4], 
			'mags':[35., 30., 25., 20., 15.], 
                        'text':['35.0','30.0','25.0','20.0','15.0']}) 
plot.state.text('x','y','text', source=mag_label_source, text_font_size='11pt', text_color='deepskyblue', text_align='right')
plot.state.text([3.8],[5+0.7],['Apparent'], text_font_size='11pt', text_color='deepskyblue', text_align='right')
plot.state.text([3.8],[5+0.2],['Mag'], text_font_size='11pt', text_color='deepskyblue', text_align='right')
plot.state.text([3.2],[5+0.2],['S/N'], text_font_size='11pt', text_color='red', text_align='right')

initial_crowding_limit = -12.5 
confusion_limit_source = ColumnDataSource(data={'top':[initial_crowding_limit], 'textx':[-0.8],  
                                                'texty':[initial_crowding_limit-0.2], 'text':['Crowding: 390 stars sq. arcsec)']}) 
plot.state.quad(top='top', bottom=-13.0, left=-1.2, right=4.0, source=confusion_limit_source, fill_alpha=0.2,  
                  fill_color='black', line_alpha=0.2, line_width=1, line_color='black') 
plot.state.text('textx', 'texty', 'text', source=confusion_limit_source, text_align='left', text_color='black') 

###########################################
# CREATE THE SYOTOOLS ELEMENTS AND MODELS # 
###########################################
e, c, t = PhotometricExposure(), Camera(), Telescope()
t.add_camera(c)
t.aperture = 15.0 * u.meter 
c.add_exposure(e)
e.sed_id = 'fab'
t.aperture = 15. * u.meter 
e.exptime = 3600. * u.s 

new_snrs = np.arange(5) # derives the S/N at various magnitude limits 
for ii in [0,1,2,3,4]:
    e.renorm_sed(mag_label_source.data['mags'][ii] * u.ABmag) 	
    new_snrs[ii] = e.snr[1]['value'][4] 

# results of ETC are stored weirdly as a list of AB mags = e.magnitude[1]['value'][:] 
etc_label_source = ColumnDataSource(data={'mags': mag_label_source.data['mags'], 'snr': new_snrs, 'snr_label': new_snrs.astype('|S4'), 
					'x': [3.2, 3.2, 3.2, 3.2, 3.2], 'y': [-10-0.4,-5-0.4,0-0.4,5-0.4,10-0.4]  }) 
plot.state.text('x','y','snr_label', source=etc_label_source, text_font_size='11pt', text_color='red', text_align='right')

limiting_mag_source = ColumnDataSource(data={'mags': [-10.], 'maglabel':[str(30.)], 'sn':[str(5.)], 'x_mag':[3.8], 'x_sn':[3.2]}) 
plot.state.text('x_mag','mags','maglabel', source=limiting_mag_source, text_font_size='11pt', text_color='deepskyblue', text_align='right')
plot.state.text('x_sn','mags','sn', source=limiting_mag_source, text_font_size='11pt', text_color='red', text_align='right')

###########################################
#         CONTROLS AND CALLBACKS          #
###########################################

def age_slider_update(attrname, old, new):             
    # this dictionary is necessary because the table of values often have non-exact age values, e.g. 9.45000001 
    age_slider_dict = {'9.1':72,'9.15':73, '9.2':74, '9.25':75, '6':10, '7':30,'8':50,'9':70,'10':90} 
    age_list = np.arange(94) * 0.05 + 5.5
    for entry, integer in zip(age_list, np.arange(94)): 
        age_slider_dict[str(entry)] = integer 
    age_stream.event(age=age_slider_dict[str(new)]) 

def metallicity_slider_update(attrname, old, new):             
    metallicity_slider_dict = {'-2.0':0, '-2':0, '-1.5':1, '-1.0':2, '-1':2, '-0.5':3, '0.0':4, '0':4} 
    print('metallicity selected by slider = ', metallicity_slider_dict[str(metallicity_slider.value)]) 
    metallicity_stream.event(metallicity=metallicity_slider_dict[str(metallicity_slider.value)])

def noise_slider_update(attrname, old, new):             
    print("Inside noise_slider, will scale to: ", noise_slider.value) 
    noise_stream.event(noise=int(noise_slider.value))

def distance_slider_update(attrname, old, new):             
    distmod = 5. * np.log10((new+1e-5) * 1e6) - 5. 
    mag_label_source.data['mags'] = distmod+np.array([10.,5.,0.,-5.,-10.])
    mag_label_source.data['text'] = mag_label_source.data['mags'].astype('|S4')

    print('calling noise_stream in distance slider') 
    noise_stream.event(noise=int(new * 40.))

def crowding_slider_update(attrname, old, new):             

    metallicity_slider_dict = {'-2.0':0, '-2':0, '-1.5':1, '-1.0':2, '-1':2, '-0.5':3, '0.0':4, '0':4} 
    metallicity_index_to_select = metallicity_slider_dict[str(metallicity_slider.value)]
 
    age_slider_dict = {'9.1':72,'9.15':73, '9.2':74, '9.25':75, '6':10, '7':30,'8':50,'9':70,'10':90} 
    age_list = np.arange(94) * 0.05 + 5.5
    for entry, integer in zip(age_list, np.arange(94)): 
        age_slider_dict[str(entry)] = integer 
    age_index_to_select = age_slider_dict[str(age_slider.value)]

    new_frame = cmd_frame.loc[lambda cmd_frame: (cmd_frame.metalindex == metallicity_index_to_select) & (cmd_frame.ageindex == age_index_to_select)]
    number_of_stars_per_arcsec = int(10. * (aperture_slider.value / 2.4)**2) 
    crowding_limit = crowd.get_crowding_limit(crowding_slider.value, aperture_slider.value, distance_slider.value, new_frame)
    confusion_limit_source.data = {'top':[-1. * crowding_limit], 'textx':[-0.8], 'texty':[-1.*crowding_limit-0.2], 'text':['Crowding: ('+str(number_of_stars_per_arcsec)+' stars / sq. arsec)']}  

def exposure_update(attrname, old, new):             
    print("calling exposure update with aperture = ", aperture_slider.value, '   and exptime = ', exptime_slider.value) 
    t.aperture = aperture_slider.value * u.meter 
    e.exptime = exptime_slider.value * 3600. * u.s 
    e.unknown = 'snr' 
    
    new_snrs = np.arange(5) 
    for ii in [0,1,2,3,4]:
        e.renorm_sed(mag_label_source.data['mags'][ii] * u.ABmag) 	
        new_snrs[ii] = e.snr[1]['value'][4] 
    
    etc_label_source.data = {'mags': mag_label_source.data['mags'], 
                             'snr': new_snrs, 
                             'snr_label': new_snrs.astype('|S4'), 
			     'x': map(lambda n: 3.2, range(5)), 				
			     'y': [-10-0.4,-5-0.4,0-0.4,5-0.4,10-0.4]  }  		        
    noise_stream.event(noise=int(noise_slider.value))

def sn_slider_update(attrname, old, new):             
    print("calling sn_updater with sn= ", sn_slider.value, '   and exptime = ', exptime_slider.value) 
    t.aperture = aperture_slider.value * u.meter 
    e.exptime = exptime_slider.value * 3600. * u.s 
    e.snr = sn_slider.value * u.electron**0.5
    e.unknown = 'magnitude' 
    vmag = e.magnitude[1]['value'][4]
    distmod = 5. * np.log10((distance_slider.value+1e-5) * 1e6) - 5. 
    limiting_mag_source.data = {'mags':[distmod-vmag-0.4],'maglabel':[str(vmag)[0:4]],'sn':[str(sn_slider.value)],'x_mag':[3.8],'x_sn':[3.2]} # the 0.4 is just for display purposes (text alignment) 
    
fake_callback_source1 = ColumnDataSource(data=dict(value=[]))
fake_callback_source1.on_change('data', exposure_update)
fake_callback_source1.on_change('data', sn_slider_update)

fake_callback_source2 = ColumnDataSource(data=dict(value=[])) # for S/N 
fake_callback_source2.on_change('data', sn_slider_update)

fake_callback_source3 = ColumnDataSource(data=dict(value=[])) 
fake_callback_source3.on_change('data', noise_slider_update)

astro_controls = [] 
exposure_controls = [] 
visual_controls = [widget] 

age_slider = Slider(start=5.5, end=10.15, value=10., step=0.05, title="Log(Age in Gyr)", callback_policy='mouseup')
age_slider.on_change('value', age_slider_update)
astro_controls.append(age_slider) 

metallicity_slider = Slider(start=-2., end=0.0, value=0., step=0.5, title="Log(Z/Zsun)")
metallicity_slider.on_change('value', metallicity_slider_update)
astro_controls.append(metallicity_slider) 

distance_slider = Slider(start=0.0, end=20., value=1., step=0.5, title="Distance [Mpc]")
distance_slider.on_change('value', distance_slider_update)
distance_slider.on_change('value', exposure_update)
distance_slider.on_change('value', sn_slider_update)
distance_slider.on_change('value', crowding_slider_update)
astro_controls.append(distance_slider) 

crowding_slider = Slider(start=15, end=35., value=20., step=0.1, title="Surface Brightness [AB/asec^2]") 
crowding_slider.on_change('value', crowding_slider_update)
astro_controls.append(crowding_slider) 

aperture_slider = Slider(start=1, end=20, value=15, step=1, title="Aperture [meters]")
aperture_slider.on_change('value', exposure_update)
exposure_controls.append(aperture_slider) 

exptime_slider = Slider(title="Exptime [hours]", value=1., start=0.1, end=50.0, step=0.1, callback_policy='mouseup') 
exptime_slider.callback = CustomJS(args=dict(source=fake_callback_source1), code="""
    source.data = { value: [cb_obj.value] }
""")
exposure_controls.append(exptime_slider) 

sn_slider = Slider(title="S/N for limiting mag", value=5., start=1.0, end=100.0, step=1.0, callback_policy='mouseup') 
sn_slider.callback = CustomJS(args=dict(source=fake_callback_source2), code="""
    source.data = { value: [cb_obj.value] }
""")
exposure_controls.append(sn_slider) 

noise_slider = Slider(title="Noise to Add In", value=500, start=0.0, end=1000.0, step=50.0, callback_policy='mouseup') 
noise_slider.callback = CustomJS(args=dict(source=fake_callback_source3), code="""
    source.data = { value: [cb_obj.value] }
""")
exposure_controls.append(noise_slider) 

sp.set_plot_options(plot.state) # plot.state has bokeh type Figure, so can be manipulated in the usual way 

astro_tab = Panel(child=Column(children=astro_controls), title='Stars') 
exposure_tab = Panel(child=Column(children=exposure_controls), title='Exposure') 
info_tab = Panel(child=Div(text = h.help(), width=300), title='Info') 
visual_tab = Panel(child=Column(children=[widget]), title='Visuals') 
controls = Tabs(tabs=[astro_tab, exposure_tab, visual_tab, info_tab], width=400)

layout = layout([[controls, plot.state]], sizing_mode='fixed')
curdoc().add_root(layout)
