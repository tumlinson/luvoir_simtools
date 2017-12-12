from __future__ import print_function
import numpy as np
import math 
from astropy.table import Table 
import copy  
import os 

import multiplanet_help as h 
import get_yield_for_cds as gy 
import get_tooltip 

from bokeh.io import curdoc 
from bokeh.plotting import Figure
from bokeh.driving import bounce 
from bokeh.models import ColumnDataSource, HoverTool, Range1d, Square, Circle
from bokeh.layouts import Column, Row
from bokeh.models.widgets import Panel, Tabs, Slider, Div, Button, DataTable, DateFormatter, TableColumn 
from bokeh.models.callbacks import CustomJS

cwd = os.getenv('LUVOIR_SIMTOOLS_DIR')

yields = gy.get_yield('12.0', '-10') # this is the starting yield set, 12 m with contrast = 1e-10 
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

plot2 = Figure(plot_height=800, plot_width=800, x_axis_type = None, y_axis_type = None,
              tools="pan,reset,save,tap,box_zoom,wheel_zoom", outline_line_color='white', 
              x_range=[-50, 50], y_range=[-50, 50], toolbar_location='right')
image1 = 'http://www.stsci.edu/~tumlinso/stark_luvoir_yields/tumlinson-multiplanet_results-12.0_1.00E-10_0.10_3.0/HIP_9829.png'
plot2.image_url(url=[image1], x=[-50], y=[50], w=100, h=130)
plot2.border_fill_color = "white"
plot2.background_fill_color = "white"


star_syms = plot1.circle('x', 'y', source=star_points, name="star_points_to_hover", \
      fill_color='color', line_color='color', radius=0.5, line_alpha='alpha', fill_alpha='alpha')
star_syms.selection_glyph = Circle(fill_alpha=0.8, fill_color="gold", radius=1.5, line_color='purple', line_width=3)

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
 			               str(star_points.data['complete8'][inds])[0:6]] 

    # now change the image in the "Star" tab to show the selected star  
    print('You have selected star HIP', star_points.data['hip'][inds]) 
    print('You have a telescope of size: ', str(aperture.value * 10. / 10.)) 
    print('You have a telescope with contrast: ', contrast.value) 
    image_prefix = 'http://www.stsci.edu/~tumlinso/stark_luvoir_yields/tumlinson-multiplanet_results-'+ \
                       str(aperture.value*10./10.)+'_1.00E'+str(contrast.value)+'_0.10_3.0/' 
    image_file = 'HIP_'+str(int(star_points.data['hip'][inds]))+'.png' 
    print('I need to go get file: ', image_prefix + image_file) 
    plot2.image_url(url=[image_prefix+image_file], x=[-50], y=[50], w=100, h=130)
    

star_syms.data_source.on_change('selected', SelectCallback)

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

# second plot, the bar chart of yields
hist_plot = Figure(plot_height=400, plot_width=480, tools="reset,save,tap", outline_line_color='black', \
                x_range=[-0.1,3], y_range=[0,300], toolbar_location='below', x_axis_type = None, 
                title='Expected Total Yield in One Year Survey') 
hist_plot.title.text_font_size = '14pt'
hist_plot.background_fill_color = "white"
hist_plot.background_fill_alpha = 1.0
hist_plot.yaxis.axis_label = 'X'
hist_plot.yaxis.axis_label_text_font= 'PT Serif' 
hist_plot.yaxis.major_label_text_font = 'PT Serif' 
hist_plot.xaxis.axis_label = 'Y'
hist_plot.xaxis.axis_line_width = 2
hist_plot.yaxis.axis_line_width = 2
hist_plot.xaxis.axis_line_color = 'black'
hist_plot.yaxis.axis_line_color = 'black'
hist_plot.border_fill_color = "white"
hist_plot.min_border_left = 0
hist_plot.image_url(url=["http://jt-astro.science/luvoir_simtools/data/planets.jpg"], x=[-0.05], y=[305], w=[3.0], h=[305])
hist_plot.text([0.45], [280], ['Rocky'], text_align='center') 
hist_plot.text([1.45], [280], ['Neptunes'], text_align='center') 
hist_plot.text([2.45], [280], ['Jupiters'], text_align='center') 
hist_plot.title.align='center' 
hist_plot.title.text_font='PT Serif' 

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
hist_plot.quad(top='yields', bottom=0., left='left', right='right', source=total_yield_label, \
                color='color', fill_alpha=0.9, line_alpha=1., name='total_yield_label_hover')
           
hist_plot.text('left', 'yields', 'labels', 0., 20, -3, text_align='center', source=total_yield_label, text_color='black')

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

def update_data(attrname, old, new):

    print('APERTURE A = ', aperture.value, ' CONTRAST C = ', contrast.value, ' IWA I = ', iwa.value) 
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
    print(total_yield_label.data['labels']) 
 
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
    print('NSTARS INSIDE UPDATE DATA', n_stars, iran) 
    new_dict = {'x': yields['x'][iran], 'y':yields['y'][iran], 'r':0.8+0.0*yields['y'][iran], 'color':col[iran], 'alpha':np.array(alph)[iran]} 
    pulse_points.data = new_dict  

def recalc(): 
    # NOW DRAW RANDOM VARIATES TO GET HIGHLIGHTED STARS
    col = copy.deepcopy(yields['stype']) 
    col[:] = 'deepskyblue'
    alph = copy.deepcopy(yields['x']) 
    alph[:] = 1.
    n_stars = np.size(yields['complete1'])  
    random_numbers = np.random.random(n_stars) 
    indices = np.arange(n_stars) 
    iran = np.array(indices[ random_numbers < star_points.data['complete1'] ]) 
    new_dict = {'x': star_points.data['x'][iran], 'y':star_points.data['y'][iran], 'r':0.8+0.0*star_points.data['y'][iran], 'color':col[iran], 'alpha':np.array(alph)[iran]} 
    pulse_points.data = new_dict  


# Make the blue stars pulse 
@bounce([0,0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9])
def pulse_stars(i):
    pulse_points.data['alpha'] = np.array(pulse_points.data['alpha']) * 0. + 1. * i 
    pulse_points.data['r'] = np.array(pulse_points.data['alpha']) * 0. + (0.3 * i + 0.5) 
    
# Set up widgets with "fake" callbacks 
source = ColumnDataSource(data=dict(value=[]))
source.on_change('data', update_data)
aperture= Slider(title="Aperture (meters)", value=12., start=4., end=20.0, step=4.0, callback_policy='mouseup', width=450)
aperture.callback = CustomJS(args=dict(source=source), code="""
    source.data = { value: [cb_obj.value] }
""")
contrast = Slider(title="Log (Contrast)", value=-10, start=-11.0, end=-9, step=1.0, callback_policy='mouseup', width=450)
contrast.callback = CustomJS(args=dict(source=source), code="""
    source.data = { value: [cb_obj.value] }
""")
iwa = Slider(title="Inner Working Angle (l/D)", value=1.5, start=1.5, end=4.0, step=0.5, callback_policy='mouseup', width=450)
iwa.callback = CustomJS(args=dict(source=source), code="""
    source.data = { value: [cb_obj.value] }
""")
regenerate = Button(label='Regenerate the Sample of Detected Candidates', width=450, button_type='success') 
regenerate.on_click(recalc) 

#######

eta_table_data = dict(
        ptype=['Hot Rock', 'Warm Rock', 'Cold Rock', 'Hot Neptunes', 'Warm Neptunes', 'Cold Neptunes','Hot Jupiters','Warm Jupiters','Cold Jupiters'], 
        radii=['0.5-1.4','0.5-1.4','0.5-1.4','1.4-4','1.4-4','1.4-4','4-11.6','4-11.6','4-11.6'], 
        eta=['0.82','0.41','0.41','0.69','0.35','0.35','0.09','0.09','0.09'], 
        a=['0.074-0.816','0.816-1.62','1.62-12.4','0.735-0.791','0.791-1.54','1.54-12.4','0.0735-0.803','0.803-1.58','1.58-13.5'] 
    )
eta_table_source = ColumnDataSource(eta_table_data)
eta_columns = [
        TableColumn(field="ptype", title="Planet Type"), 
        TableColumn(field="radii", title="R/R_Earth"),
        TableColumn(field="eta", title="Eta")] 
eta_table = DataTable(source=eta_table_source, columns=eta_columns, width=450, height=980)

#######


# Set up control widgets and their layout 
input_sliders = Column(children=[aperture, contrast, regenerate]) 
control_tab = Panel(child=input_sliders, title='Controls', width=450)
div = Div(text=h.help(),width=450, height=2000)
info_tab = Panel(child=div, title='Info', width=450, height=300)
eta_tab = Panel(child=eta_table, title='Planets', width=450, height=300)
plot1_tab = Panel(child=plot1, title='View', width=800, height=800)
plot2_tab = Panel(child=plot2, title='Star', width=800, height=800)
input_tabs = Tabs(tabs=[control_tab,info_tab,eta_tab], width=450)  
inputs = Column(hist_plot, input_tabs) 
plot_tabs = Tabs(tabs=[plot1_tab, plot2_tab], width=800)  
rowrow =  Row(inputs, plot_tabs)  

curdoc().add_root(rowrow) # Set up layouts and add to document
curdoc().add_root(source) 
curdoc().add_periodic_callback(pulse_stars, 100)
