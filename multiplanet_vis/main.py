from __future__ import print_function
import numpy as np
from astropy.table import Table 
import copy  
import os 

import multiplanet_help as h 
import get_yield_for_cds as gy 
import get_tooltip 

from bokeh.io import curdoc 
from bokeh.plotting import Figure
from bokeh.driving import bounce 
from bokeh.models import ColumnDataSource, HoverTool, Circle
from bokeh.layouts import Column, Row
from bokeh.models.widgets import Panel, Tabs, Slider, Div, Button, DataTable, DateFormatter, TableColumn, StringFormatter
from bokeh.models.callbacks import CustomJS

import multiplanet_plot_options as sp, eta_table as et 

cwd = os.getenv('LUVOIR_SIMTOOLS_DIR')

yields = gy.get_yield('12.0', '-10') # this is the starting yield set, 12 m with contrast = 1e-10, returns a dictionary 
star_points = ColumnDataSource(data = yields)  
#star_points.data['x'][[star_points.data['color'] == 'black']] += 2000. 	# this line shifts the black points with no yield off the plot 

# set up the main plot and do its tweaks 
bullseye_plot = Figure(plot_height=800, plot_width=800, x_axis_type = None, y_axis_type = None,
              tools="pan,reset,save,tap,box_zoom,wheel_zoom", outline_line_color='#1D1B4D', 
              x_range=[-50, 50], y_range=[-50, 50], toolbar_location='right')
hover = HoverTool(names=["star_points_to_hover"], mode='mouse', tooltips = get_tooltip.tooltip()) 
bullseye_plot.add_tools(hover) 
hover = bullseye_plot.select(dict(type=HoverTool))
sp.set_bullseye_plot_options(bullseye_plot)

star_syms = bullseye_plot.circle('x', 'y', source=star_points, name="star_points_to_hover", \
      fill_color='color', line_color='color', radius=0.5, line_alpha='alpha', fill_alpha='alpha')
star_syms.selection_glyph = Circle(fill_alpha=0.8, fill_color="#F59A0A", radius=2.0, line_color='#BAD8FF', line_width=2)

# this is not currently being used - it is intended to show the image of each system 
plot2 = Figure(plot_height=800, plot_width=800, x_axis_type = None, y_axis_type = None,
              tools="pan,reset,save,tap,box_zoom,wheel_zoom", outline_line_color='white', 
              x_range=[-50, 50], y_range=[-50, 50], toolbar_location='right', border_fill_color='white', background_fill_color='white')
image1 = 'http://www.stsci.edu/~tumlinso/stark_luvoir_yields/tumlinson-multiplanet_results-12.0_1.00E-10_0.10_3.0/HIP_9829.png'
plot2.image_url(url=[image1], x=[-50], y=[50], w=100, h=130)

def SelectCallback(attrname, old, new): 
    inds = np.array(new['1d']['indices'])[0] # this miraculously obtains the index of the slected star within the star_syms CDS 
    star_yield_label.data['labels'] = [str(star_points.data['complete0'][inds])[0:6], \
 			               str(star_points.data['complete1'][inds])[0:6], \
 			               str(star_points.data['complete2'][inds])[0:6], \
 			               str(star_points.data['complete3'][inds])[0:6], \
 			               str(star_points.data['complete4'][inds])[0:6], \
 			               str(star_points.data['complete5'][inds])[0:6], \
 			               str(star_points.data['complete6'][inds])[0:6], \
 			               str(star_points.data['complete7'][inds])[0:6], \
 			               str(star_points.data['complete8'][inds])[0:6], \
 			               str(star_points.data['complete9'][inds])[0:6], \
 			               str(star_points.data['complete10'][inds])[0:6], \
 			               str(star_points.data['complete11'][inds])[0:6], \
 			               str(star_points.data['complete12'][inds])[0:6], \
 			               str(star_points.data['complete13'][inds])[0:6], \
 			               str(star_points.data['complete14'][inds])[0:6]] 

    # now change the image in the "Star" tab to show the selected star  
    print('You have selected star STARID', star_points.data['starid'][inds]) 
    print('You have a telescope of size: ', str(aperture.value * 10. / 10.)) 
    print('You have a telescope with contrast: ', contrast.value) 
    image_prefix = 'http://www.stsci.edu/~tumlinso/stark_luvoir_yields/tumlinson-multiplanet_results-'+ \
                       str(aperture.value*10./10.)+'_1.00E'+str(contrast.value)+'_0.10_3.0/' 
    image_file = 'starid_'+str(int(star_points.data['hip'][inds]))+'.png' 
    print('I need to go get file: ', image_prefix + image_file) 
    plot2.image_url(url=[image_prefix+image_file], x=[-50], y=[50], w=100, h=130)

star_syms.data_source.on_change('selected', SelectCallback)

sym = bullseye_plot.circle(np.array([0., 0., 0., 0.]), np.array([0., 0., 0., 0.]), fill_color='#1D1B4D', line_color='white', 
           line_width=4, radius=[40,30,20,10], line_alpha=0.8, fill_alpha=0.0) 
sym.glyph.line_dash = [6, 6]

eta_life = 0.1 

# create pulsing symbols for detected Earths - probability given by yields 
n_stars = np.size(yields['eec_complete'])  
col = copy.deepcopy(yields['stype']) 
col[:] = '#BAD8FF'
life_col = copy.deepcopy(yields['stype']) 
life_col[:] = 'darkgreen' 
alph = copy.deepcopy(yields['x']) 
alph[:] = 1.
random_numbers = np.random.random(n_stars) 
yields['random_variates'] = random_numbers 
indices = np.arange(n_stars) 
iearth = indices[ random_numbers < yields['eec_complete'] ] 
iliving = indices[ random_numbers < eta_life * yields['eec_complete'] ] 
earth_points=ColumnDataSource(data={'x':yields['x'][iearth],'y':yields['y'][iearth],'r':0.8+0.0*yields['y'][iearth],'color':col[iearth],'alpha':np.array(alph)[iearth]}) 
earth_syms = bullseye_plot.circle('x','y', source=earth_points, name="earth_points", fill_color='color',radius='r', line_alpha='alpha', fill_alpha='alpha')
life_points=ColumnDataSource(data={'x':yields['x'][iliving],'y':yields['y'][iliving],'r':2.0+0.0*yields['y'][iliving],'color':life_col[iliving],'alpha':np.array(alph)[iliving]}) 
life_syms = bullseye_plot.circle('x','y', source=life_points, name="life_points", fill_color='color',radius='r', line_alpha='alpha', fill_alpha='alpha') 

# second plot, the bar chart of yields
hist_plot = Figure(plot_height=330, plot_width=480, tools="reset,save,tap", outline_line_color='#1D1B4D', \
                x_range=[-0.1,5], y_range=[0,300], toolbar_location='right', x_axis_type = None, 
                title='Expected Total Yield in One Year Survey') 
sp.set_hist_plot_options(hist_plot) 

# this will place labels in the small plot for the *selected star* - not implemented yet
star_yield_label = ColumnDataSource(data=dict(yields=[10., 10., 10., 10., 10., 10., 10., 10., 10., 10., 10., 10., 10., 10., 10.],
                                        left=[0.0,0.3,0.6,  1.0,1.3,1.6,  2.0,2.3,2.6, 3.0,3.3,3.6, 4.0,4.3,4.6],
                                        right=[0.3,0.6,0.9, 1.3,1.6,1.9,  2.3,2.6,2.9, 3.3,3.6,3.9, 4.3,4.6,4.9],
                                        color=['#FB0006','#118CFF','#B7E0FF','#FB0006','#118CFF','#B7E0FF','#FB0006','#118CFF','#B7E0FF', '#FB0006','#118CFF','#B7E0FF', '#FB0006','#118CFF','#B7E0FF'],
                                        labels=["0", "0", "0", "0", "0", "0", "0", "0","0","0","0","0","0","0","0"])) 
total_yield_label = ColumnDataSource(data=dict(yields=[0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.], \
                                        left=[0.0,0.3,0.6,  1.0,1.3,1.6,  2.0,2.3,2.6, 3.0,3.3,3.6, 4.0,4.3,4.6],
                                        right=[0.3,0.6,0.9, 1.3,1.6,1.9,  2.3,2.6,2.9, 3.3,3.6,3.9, 4.3,4.6,4.9],
                                        color=['FB0006', '#118CFF', '#B7E0FF', 'FB0006', '#118CFF', '#B7E0FF', 'FB0006', '#118CFF', '#B7E0FF', 'FB0006','#118CFF','#B7E0FF', 'FB0006','#118CFF','#B7E0FF'],
                                        temp=['Hot','Warm','Cool','Hot','Warm','Cool','Hot','Warm','Cool', 'Hot','Warm','Cool', 'Hot','Warm','Cool'], 
                                        mass=['Rocky','Rocky','Rocky','SuperEarth','SuperEarth','SuperEarth',
                                              'Sub-Neptune','Sub-Neptune','Sub-Neptune','Neptunes','Neptunes','Neptunes','Jupiters','Jupiters','Jupiters'], 
                                        labels=["0","0","0","0","0","0","0","0","0","0","0","0","0","0","0"], 
                                        xlabels=np.array([0.15,0.45,0.75, 1.15,1.45,1.75, 2.15,2.45,2.75, 3.15,3.45,3.75, 4.15,4.45,4.75])-0.25 )) 
                                         
total_yield_label.data['yields'] = [np.sum(yields['complete0'][:]), np.sum(yields['complete1'][:]), 
                                        np.sum(yields['complete2'][:]), np.sum(yields['complete3'][:]), 
                                        np.sum(yields['complete4'][:]), np.sum(yields['complete5'][:]), 
                                        np.sum(yields['complete6'][:]), np.sum(yields['complete7'][:]), 
                                        np.sum(yields['complete8'][:]), np.sum(yields['complete9'][:]), 
                                        np.sum(yields['complete10'][:]), np.sum(yields['complete11'][:]), 
                                        np.sum(yields['complete12'][:]), np.sum(yields['complete13'][:]), 
                                        np.sum(yields['complete14'][:])] 
total_yield_label.data['labels'] = [str(int(np.sum(yields['complete0'][:]))), str(int(np.sum(yields['complete1'][:]))), 
                                        str(int(np.sum(yields['complete2'][:]))), str(int(np.sum(yields['complete3'][:]))), 
                                        str(int(np.sum(yields['complete4'][:]))), str(int(np.sum(yields['complete5'][:]))), 
                                        str(int(np.sum(yields['complete6'][:]))), str(int(np.sum(yields['complete7'][:]))), 
                                        str(int(np.sum(yields['complete8'][:]))), str(int(np.sum(yields['complete9'][:]))),
                                        str(int(np.sum(yields['complete10'][:]))), str(int(np.sum(yields['complete11'][:]))),
                                        str(int(np.sum(yields['complete12'][:]))), str(int(np.sum(yields['complete13'][:]))),
                                        str(int(np.sum(yields['complete14'][:])))] 

hist_plot.quad(top='yields', bottom=0., left='left', right='right', source=total_yield_label, \
                color='color', fill_alpha=0.9, line_alpha=1., name='total_yield_label_hover')
           
hist_plot.text('xlabels', 'yields', 'labels', 0., 20, -3, text_align='center', source=total_yield_label, text_color='black')

yield_hover = HoverTool(names=["total_yield_label_hover"], mode='mouse', tooltips = """ 
            <div>
                <span style="font-size: 20px; font-weight: bold; color:@color">N = </span>
                <span style="font-size: 20px; font-weight: bold; color:@color">@yields</span>
            </div>
            <div>
                <span style="font-size: 20px; font-weight: bold; color:@color">@temp </span>
            </div>
            <div>
                <span style="font-size: 20px; font-weight: bold; color:@color">@mass</span>
            </div>
              """) 
hist_plot.add_tools(yield_hover) 



def helper_func(aperture, contrast, eta_life, method_switch): 

    print('APERTURE A = ', aperture, ' CONTRAST C = ', contrast, 'Eta_life = ', eta_life) 
    yields = gy.get_yield(aperture, contrast) 
    star_points.data = yields 
    
    total_yield_label.data['yields'] = [np.sum(yields['complete0'][:]), np.sum(yields['complete1'][:]), 
                                        np.sum(yields['complete2'][:]), np.sum(yields['complete3'][:]), 
                                        np.sum(yields['complete4'][:]), np.sum(yields['complete5'][:]), 
                                        np.sum(yields['complete6'][:]), np.sum(yields['complete7'][:]), 
                                        np.sum(yields['complete8'][:]), np.sum(yields['complete9'][:]), 
                                        np.sum(yields['complete10'][:]), np.sum(yields['complete11'][:]), 
                                        np.sum(yields['complete12'][:]), np.sum(yields['complete12'][:]), 
                                        np.sum(yields['complete14'][:])] 
    total_yield_label.data['labels'] = [str(int(np.sum(yields['complete0'][:]))), str(int(np.sum(yields['complete1'][:]))), 
                                        str(int(np.sum(yields['complete2'][:]))), str(int(np.sum(yields['complete3'][:]))), 
                                        str(int(np.sum(yields['complete4'][:]))), str(int(np.sum(yields['complete5'][:]))), 
                                        str(int(np.sum(yields['complete6'][:]))), str(int(np.sum(yields['complete7'][:]))), 
                                        str(int(np.sum(yields['complete8'][:]))), str(int(np.sum(yields['complete9'][:]))),
                                        str(int(np.sum(yields['complete10'][:]))), str(int(np.sum(yields['complete11'][:]))),
                                        str(int(np.sum(yields['complete12'][:]))), str(int(np.sum(yields['complete13'][:]))),
                                        str(int(np.sum(yields['complete14'][:])))] 

    # regenerate the pulsing blue points 
    col = copy.deepcopy(yields['stype']) 
    col[:] = '#BAD8FF'
    life_col = copy.deepcopy(yields['stype']) 
    life_col[:] = 'darkgreen'
    alph = copy.deepcopy(yields['x']) 
    alph[:] = 1.

    n_stars = np.size(yields['eec_complete'])  
    random_numbers = np.random.random(n_stars) 
    indices = np.arange(n_stars) 
    #three cases
    if ('nothing' in method_switch): 
        iearth = indices[ yields['random_variates'] < yields['eec_complete'] ] # use the random variates that come with this yield dictionary instead of a new one 
        iliving = indices[ yields['random_variates'] < eta_life * yields['eec_complete'] ]
    if ('shuffle'): 
        iearth = indices[ random_numbers  < yields['eec_complete'] ] # use the random variates that come with this yield dictionary instead of a new one 
        iliving = indices[ random_numbers < eta_life * yields['eec_complete'] ]
        yields['random_variates'] = random_numbers 
    if ('eta'): 
        iearth = indices[ yields['random_variates'] < yields['eec_complete'] ] # use the random variates that come with this yield dictionary instead of a new one 
        iliving = indices[ random_numbers < eta_life * yields['eec_complete'] ]
    new_dict = {'x': yields['x'][iearth], 'y':yields['y'][iearth], 'r':0.8+0.0*yields['y'][iearth], 'color':col[iearth], 'alpha':np.array(alph)[iearth]} 
    newer_dict = {'x': yields['x'][iliving], 'y':yields['y'][iliving], 'r':0.8+0.0*yields['y'][iliving], 'color':life_col[iliving], 'alpha':np.array(alph)[iliving]} 
    earth_points.data = new_dict  
    life_points.data = newer_dict 

def update_data(attrname, old, new):
    helper_func(aperture.value, contrast.value, eta_life.value, 'nothing') 

def recalc_data(): 
    helper_func(aperture.value, contrast.value, eta_life.value, 'shuffle') 

def update_eta(attrname, old, new):
    helper_func(aperture.value, contrast.value, eta_life.value, 'eta') 

   



if(False): 
    def update_dead(attrname, old, new):
    
        print('APERTURE A = ', aperture.value, ' CONTRAST C = ', contrast.value, ' IWA I = ', iwa.value, "Eta_life = ", eta_life.value) 
        yields = gy.get_yield(aperture.value, contrast.value) 
        star_points.data = yields 
    
        total_yield_label.data['yields'] = [np.sum(yields['complete0'][:]), np.sum(yields['complete1'][:]), 
                                            np.sum(yields['complete2'][:]), np.sum(yields['complete3'][:]), 
                                            np.sum(yields['complete4'][:]), np.sum(yields['complete5'][:]), 
                                            np.sum(yields['complete6'][:]), np.sum(yields['complete7'][:]), 
                                            np.sum(yields['complete8'][:]), np.sum(yields['complete9'][:]), 
                                            np.sum(yields['complete10'][:]), np.sum(yields['complete11'][:]), 
                                            np.sum(yields['complete12'][:]), np.sum(yields['complete12'][:]), 
                                            np.sum(yields['complete14'][:])] 
        total_yield_label.data['labels'] = [str(int(np.sum(yields['complete0'][:]))), str(int(np.sum(yields['complete1'][:]))), 
                                            str(int(np.sum(yields['complete2'][:]))), str(int(np.sum(yields['complete3'][:]))), 
                                            str(int(np.sum(yields['complete4'][:]))), str(int(np.sum(yields['complete5'][:]))), 
                                            str(int(np.sum(yields['complete6'][:]))), str(int(np.sum(yields['complete7'][:]))), 
                                            str(int(np.sum(yields['complete8'][:]))), str(int(np.sum(yields['complete9'][:]))),
                                            str(int(np.sum(yields['complete10'][:]))), str(int(np.sum(yields['complete11'][:]))),
                                            str(int(np.sum(yields['complete12'][:]))), str(int(np.sum(yields['complete13'][:]))),
                                            str(int(np.sum(yields['complete14'][:])))] 
    
    
    def update_eta(attrname, old, new):
        # HERE WE WILL RESAMPLE BASED ON ETA LIFE WITHOUT CHANGING THE ETA_EARTH 
        # OOPS - FOR SOME REASON THIS ALWYAS USES THE 12 M yield until it is regenerate!!! 
    
        #FIX THIS HERE SO AS NOT TO RESAMPLE ALL THE YIELDS WITH ETA CHANGES!!!!! 
    
        print('ETA LIFE IN UPDATE ETA', eta_life.value) 
        indices = np.arange(n_stars) 
        iearth = indices[ yields['random_variates'] < yields['eec_complete'] ] 
        iliving = indices[ random_numbers < eta_life.value * yields['eec_complete'] ]
        new_dict = {'x': yields['x'][iearth], 'y':yields['y'][iearth], 'r':0.8+0.0*yields['y'][iearth], 'color':col[iearth], 'alpha':np.array(alph)[iearth]} 
        newer_dict = {'x': yields['x'][iliving], 'y':yields['y'][iliving], 'r':0.8+0.0*yields['y'][iliving], 'color':life_col[iliving], 'alpha':np.array(alph)[iliving]} 
        earth_points.data = new_dict  
        life_points.data = newer_dict 
    
    def recalc(): 
        update_data('barf', 0.0, 0.0) 


# Make the blue stars pulse 
@bounce([0,0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9])
def pulse_stars(i):
    life_points.data['alpha'] = np.array(life_points.data['alpha']) * 0. + 1. * i 
    life_points.data['r'] = np.array(life_points.data['alpha']) * 0. + (0.3 * i + 0.5) 
    
# Set up widgets with "fake" callbacks 
fake_callback_source1 = ColumnDataSource(data=dict(value=[]))
fake_callback_source1.on_change('data', update_data)
aperture = Slider(title="Aperture (meters)", value=12., start=4., end=20.0, step=4.0, callback_policy='mouseup', width=400)
aperture.callback = CustomJS(args=dict(source=fake_callback_source1), code="""
    source.data = { value: [cb_obj.value] }
""")
contrast = Slider(title="Log (Contrast)", value=-10, start=-11.0, end=-9, step=1.0, callback_policy='mouseup', width=400)
contrast.callback = CustomJS(args=dict(source=fake_callback_source1), code="""
    source.data = { value: [cb_obj.value] }
""")
iwa = Slider(title="Inner Working Angle (l/D)", value=1.5, start=1.5, end=4.0, step=0.5, callback_policy='mouseup', width=400)
iwa.callback = CustomJS(args=dict(source=fake_callback_source1), code="""
    source.data = { value: [cb_obj.value] }
""")
fake_callback_source2 = ColumnDataSource(data=dict(value=[]))
fake_callback_source2.on_change('data', update_eta)
eta_life = Slider(title="Probability of Life", value=0.1, start=0.01, end=1.0, step=0.01, callback_policy='mouseup', width=400)
eta_life.callback = CustomJS(args=dict(source=fake_callback_source2), code="""
    source.data = { value: [cb_obj.value] }
""")
regenerate = Button(label='Regenerate the Sample of Detected Candidates', width=400, button_type='success') 
regenerate.on_click(recalc_data) 

# create the table of planet bins
eta_table_source = ColumnDataSource(et.eta_table())
eta_columns = [
        TableColumn(field="ptype", title="Planet Type", formatter=StringFormatter(text_color='#000000')), 
        TableColumn(field="radii", title="R/R_Earth", formatter=StringFormatter(text_color='#000000')),
        TableColumn(field="a", title="a", formatter=StringFormatter(text_color='#000000')), 
        TableColumn(field="eta", title="Eta", formatter=StringFormatter(text_color='#000000'))] 
eta_table = DataTable(source=eta_table_source, columns=eta_columns, width=450, height=980)

# Set up control widgets and their layout 
input_sliders = Column(children=[aperture, contrast, eta_life, regenerate]) 
control_tab = Panel(child=input_sliders, title='Controls', width=450)
div = Div(text=h.help(),width=450, height=2000)
info_tab = Panel(child=div, title='Info', width=450, height=300)
eta_tab = Panel(child=eta_table, title='Planets', width=450, height=300)
plot1_tab = Panel(child=bullseye_plot, title='View', width=800, height=800)
plot2_tab = Panel(child=plot2, title='Star', width=800, height=800)
input_tabs = Tabs(tabs=[control_tab,info_tab,eta_tab], width=450)  
inputs = Column(hist_plot, input_tabs) 
plot_tabs = Tabs(tabs=[plot1_tab, plot2_tab], width=800)  
rowrow =  Row(inputs, bullseye_plot)  

curdoc().add_root(rowrow) # Add layouts to document
curdoc().add_root(fake_callback_source1) 
curdoc().add_periodic_callback(pulse_stars, 50) # periodic callback to make the living planets flash 
