import numpy as np
import math 
from astropy.table import Table 
import copy  
import os 

from bokeh.io import curdoc 
from bokeh.plotting import Figure
from bokeh.driving import bounce 
from bokeh.models import ColumnDataSource, HoverTool, Range1d, Square, Circle
from bokeh.layouts import Column, Row
from bokeh.models.widgets import Panel, Tabs, Slider, Div, Button, DataTable, DateFormatter, TableColumn 
from bokeh.models.callbacks import CustomJS
from __future__ import print_function


cwd = os.getenv('LUVOIR_SIMTOOLS_DIR')

yields = gy.get_yield('12.0', '-10') # this is the starting yield set, 4 m with contrast = 1e-10 
star_points = ColumnDataSource(data = yields)  
star_points.data['x'][[star_points.data['color'] == 'black']] += 2000. 	# this line shifts the black points with no yield off the plot 

# set up the main plot and do its tweaks 
plot1 = Figure(plot_height=800, plot_width=800, x_axis_type = None, y_axis_type = None,
              tools="pan,reset,save,tap,box_zoom,wheel_zoom", outline_line_color='black', 
              x_range=[-50, 50], y_range=[-50, 50], toolbar_location='right')
hover = HoverTool(names=["star_points_to_hover"], mode='mouse', tooltips = get_tooltip.tooltip()) 
plot1.add_tools(hover) 
hover = plot1.select(dict(type=HoverTool))
plot1.x_range=Range1d(-50,50,bounds=(-50,50)) 
plot1.y_range=Range1d(-50,50,bounds=(-50,50)) 
plot1.background_fill_color = "black"
plot1.background_fill_alpha = 1.0
plot1.yaxis.axis_label = 'Yield' 
plot1.xaxis.axis_label = ' ' 
plot1.xaxis.axis_line_width = 0
plot1.yaxis.axis_line_width = 0 
plot1.xaxis.axis_line_color = 'black' 
plot1.yaxis.axis_line_color = 'black' 
plot1.border_fill_color = "black"
plot1.min_border_left = 10
plot1.min_border_right = 10

star_syms = plot1.circle('x', 'y', source=star_points, name="star_points_to_hover", \
      fill_color='color', line_color='color', radius=0.5, line_alpha='alpha', fill_alpha='alpha')
star_syms.selection_glyph = Circle(fill_alpha=0.8, fill_color="gold", radius=1.5, line_color='purple', line_width=3)

# main glyphs for planet circles  
plot1.text(0.95*0.707*np.array([10., 20., 30., 40.]), 0.707*np.array([10., 20., 30., 40.]), \
     text=['10 pc', '20 pc', '30 pc', '40 pc'], text_color="white", text_font_style='bold', text_font_size='12pt', text_alpha=0.8) 
plot1.text([48.5], [47], ['Chance Of Detecting a'], text_color="white", text_align="right") 
plot1.text([48.5], [44.5], ['Habitable Planet Candidate'], text_color="white", text_align="right") 
plot1.text([48.5], [42.0], ['if Present'], text_color="white", text_align="right") 
plot1.text([48.5], [42.0], ['___________'], text_color="white", text_align="right") 
plot1.text(np.array([48.5]), np.array([39.5]), ["80-100%"], text_color='gold', text_alpha=0.6+0.2, text_align="right") 
plot1.text(np.array([48.5]), np.array([39.5-1*2.4]), ["50-80%"], text_color='gold', text_alpha=0.3+0.2, text_align="right") 
plot1.text(np.array([48.5]), np.array([39.5-2*2.4]), ["20-50%"], text_color='gold', text_alpha=0.1+0.2, text_align="right") 
plot1.text(np.array([48.5]), np.array([39.5-3*2.4]), ["Not Observed"], text_color='black', text_align="right") 
plot1.text([-49], [46], ['Habitable Candidate Detections'], text_font_size='16pt', text_color='deepskyblue') 
plot1.text([-49], [43], ['Random Realization for One Year Survey'], text_font_size='16pt', text_color='deepskyblue') 
plot1.circle([0], [0], radius=0.1, fill_alpha=1.0, line_color='white', fill_color='white') 
plot1.circle([0], [0], radius=0.5, fill_alpha=0.0, line_color='white') 

sym = plot1.circle(np.array([0., 0., 0., 0.]), np.array([0., 0., 0., 0.]), fill_color='black', line_color='white', 
           line_width=4, radius=[40,30,20,10], line_alpha=0.8, fill_alpha=0.0) 
sym.glyph.line_dash = [6, 6]

# create pulsing symbols 
n_stars = np.size(yields['complete1'])  
col = copy.deepcopy(yields['stype']) 
col[:] = 'deepskyblue'
alph = copy.deepcopy(yields['x']) 
alph[:] = 1.
random_numbers = np.random.random(n_stars) 
indices = np.arange(n_stars) 
iran = indices[ random_numbers < yields['complete1'] ] 
pulse_points = ColumnDataSource(data={'x': yields['x'][iran], 'y':yields['y'][iran], 'r':0.8+0.0*yields['y'][iran], 'color':col[iran], 'alpha':np.array(alph)[iran]}) 
pulse_syms = plot1.circle('x','y', source=pulse_points, name="pulse_points", fill_color='color',radius='r', line_alpha='alpha', fill_alpha='alpha')



# this will place labels in the small plot for the *selected star* - not implemented yet
star_yield_label = ColumnDataSource(data=dict(yields=[10., 10., 10., 10., 10., 10., 10., 10., 10.],
                                        left=[0.0, 0.3, 0.6, 1.0, 1.3, 1.6, 2.0, 2.3, 2.6],
                                        right=[0.3, 0.6, 0.9, 1.3, 1.6, 1.9, 2.3, 2.6, 2.9],
                                        color=['red','green','blue','red','green','blue','red','green','blue'],
                                        labels=["0","0","0","0","0","0","0","0","0"],
                                        xvals =[1.5,2.5,3.5,1.5,2.5,3.5,1.5,2.5,3.5],
                                        yvals =[2.9,2.9,2.9,1.9,1.9,1.9,0.9,0.9,0.9,]))
total_yield_label = ColumnDataSource(data=dict(yields=[0., 0., 0., 0., 0., 0., 0., 0., 0.], \
                                        left=[0.0, 0.3, 0.6, 1.0, 1.3, 1.6, 2.0, 2.3, 2.6],
                                        right=[0.3, 0.6, 0.9, 1.3, 1.6, 1.9, 2.3, 2.6, 2.9],
                                        color=['red', 'green', 'blue', 'red', 'green', 'blue', 'red', 'green', 'blue'],
                                        temp=['Hot','Warm','Cool','Hot','Warm','Cool','Hot','Warm','Cool'], 
                                        mass=['Rocky','Rocky','Rocky','Neptunes','Neptunes','Neptunes','Jupiters','Jupiters','Jupiters'], 
                                        labels=["0","0","0","0","0","0","0","0","0"], \
                                        xvals =[1.5,2.5,3.5,1.5,2.5,3.5,1.5,2.5,3.5], \
                                        yvals =[2.5,2.5,2.5,1.5,1.5,1.5,0.5,0.5,0.5,]))
total_yield_label.data['yields'] = [np.sum(yields['complete0'][:]), np.sum(yields['complete1'][:]), 
                                        np.sum(yields['complete2'][:]), np.sum(yields['complete3'][:]), 
                                        np.sum(yields['complete4'][:]), np.sum(yields['complete5'][:]), 
                                        np.sum(yields['complete6'][:]), np.sum(yields['complete7'][:]), 
                                        np.sum(yields['complete8'][:])]
total_yield_label.data['labels'] = [str(int(np.sum(yields['complete0'][:]))), str(int(np.sum(yields['complete1'][:]))), 
                                        str(int(np.sum(yields['complete2'][:]))), str(int(np.sum(yields['complete3'][:]))), 
                                        str(int(np.sum(yields['complete4'][:]))), str(int(np.sum(yields['complete5'][:]))), 
                                        str(int(np.sum(yields['complete6'][:]))), str(int(np.sum(yields['complete7'][:]))), 
                                        str(int(np.sum(yields['complete8'][:])))]

def update_data(attrname, old, new):

    yields = gy.get_yield(aperture.value, contrast.value) 
    star_points.data = yields 

    total_yield_label.data['yields'] = [np.sum(yields['complete0'][:]), np.sum(yields['complete1'][:]), 
                                        np.sum(yields['complete2'][:]), np.sum(yields['complete3'][:]), 
                                        np.sum(yields['complete4'][:]), np.sum(yields['complete5'][:]), 
                                        np.sum(yields['complete6'][:]), np.sum(yields['complete7'][:]), 
                                        np.sum(yields['complete8'][:])]
    total_yield_label.data['labels'] = [str(int(np.sum(yields['complete0'][:]))), str(int(np.sum(yields['complete1'][:]))), 
                                        str(int(np.sum(yields['complete2'][:]))), str(int(np.sum(yields['complete3'][:]))), 
                                        str(int(np.sum(yields['complete4'][:]))), str(int(np.sum(yields['complete5'][:]))), 
                                        str(int(np.sum(yields['complete6'][:]))), str(int(np.sum(yields['complete7'][:]))), 
                                        str(int(np.sum(yields['complete8'][:])))]
    print total_yield_label.data['labels'] 
 
    # regenerate the pulsing blue points 
    col = copy.deepcopy(yields['stype']) 
    col[:] = 'deepskyblue'
    alph = copy.deepcopy(yields['x']) 
    alph[:] = 1.

    # NOW DRAW RANDOM VARIATES TO GET HIGHLIGHTED STARS
    n_stars = np.size(yields['complete1'])  
    random_numbers = np.random.random(n_stars) 
    indices = np.arange(n_stars) 
    iran = indices[ random_numbers < yields['complete1'] ] 
    new_dict = {'x': yields['x'][iran], 'y':yields['y'][iran], 'r':0.8+0.0*yields['y'][iran], 'color':col[iran], 'alpha':np.array(alph)[iran]} 
    pulse_points.data = new_dict  

# Make the blue stars pulse 
@bounce([0,0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9])
def pulse_stars(i):
    pulse_points.data['alpha'] = np.array(pulse_points.data['alpha']) * 0. + 1. * i 
    pulse_points.data['r'] = np.array(pulse_points.data['alpha']) * 0. + (0.3 * i + 0.5) 
    
# Set up control widgets and their layout 
input_sliders = Column(children=[aperture, contrast, regenerate]) 
control_tab = Panel(child=input_sliders, title='Controls', width=450)
div = Div(text=h.help(),width=450, height=2000)
input_tabs = Tabs(tabs=[control_tab,info_tab,eta_tab], width=450)  
inputs = Column(hist_plot, input_tabs) 
rowrow =  Row(inputs, plot1)  

curdoc().add_root(rowrow) # Set up layouts and add to document
curdoc().add_root(source) 
curdoc().add_periodic_callback(pulse_stars, 100)
