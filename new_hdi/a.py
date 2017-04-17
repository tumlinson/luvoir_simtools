''' A dead simple ETC for HDST 
'''
import numpy as np
from bokeh.io import output_file, gridplot 

import phot_compute_snr as phot_etc 

from bokeh.plotting import Figure
from bokeh.resources import CDN
from bokeh.embed import components, autoload_server 
from bokeh.models import ColumnDataSource, HBox, VBoxForm, HoverTool, Paragraph, Range1d, Square, Circle 
from bokeh.models.callbacks import CustomJS
from bokeh.layouts import column, row, WidgetBox 
from bokeh.models.widgets import Slider, Tabs, Div, Panel, Select 
from bokeh.io import hplot, vplot, curdoc
from bokeh.embed import file_html

import Telescope as T 
import hdi_help as h 
import get_hdi_seds 
import pysynphot as S 

button_plot = Figure(plot_height=240,plot_width=240, tools="tap",x_range=[0, 400], y_range=[0, 400],toolbar_location='below') 
image1 = "http://www.stsci.edu/~tumlinso/HDST_source_z2.jpg" 
image2 = "http://www.stsci.edu/~tumlinso/HST_source_z2.jpg"
button_plot.image_url(url=[image2], x=[0], y=[400], w=200, h=200, alpha=0.5) 
button_plot.image_url(url=[image2], x=[200], y=[400], w=200, h=200, alpha=0.5)
button_plot.image_url(url=[image1], x=[0], y=[200], w=200, h=200, alpha=0.5) 
button_plot.image_url(url=[image1], x=[200], y=[200], w=200, h=200, alpha=0.5)
button_source = ColumnDataSource(data=dict(tel_name=['HabEx 4','HabEx 6','LUVOIR 8','LUVOIR 16'], top=[100.,100.,50.,50.], \
                                  bottom = [50.,50.,0.,0.], left=[0.,50.,0.,50.], right=[50.,100.,50.,100.])) 
buttons = button_plot.quad(top='top', bottom='bottom', left='left', right='right', 
                 source=button_source, color='deepskyblue',alpha=0.5,name='button_hover') 
button_plot.background_fill_color = "white"
button_hover = HoverTool(point_policy="snap_to_data", 
        tooltips="""
        <div>
         <span style="font-size: 20px; font-weight: bold; color: #F00;">@tel_name</span>
        </div>
        """
    )
button_plot.add_tools(button_hover) 
button_plot.background_fill_alpha = 1.0
button_plot.yaxis.axis_label = ' '
button_plot.xaxis.axis_label = ' '
button_plot.xaxis.minor_tick_line_color = 'white'
button_plot.xaxis.major_tick_line_color = 'white'
button_plot.yaxis.minor_tick_line_color = 'white'
button_plot.yaxis.major_tick_line_color = 'white'
button_plot.xaxis.major_label_text_color= 'white'
button_plot.xaxis.axis_label_text_color= 'white'
button_plot.yaxis.major_label_text_color= 'white'
button_plot.yaxis.axis_label_text_color= 'white'
button_plot.xaxis.axis_line_width = 0
button_plot.yaxis.axis_line_width = 0
button_plot.xaxis.axis_line_color = 'white'
button_plot.yaxis.axis_line_color = 'white'
button_plot.border_fill_color = "white"
button_plot.min_border_left = 0
button_plot.min_border_right = 0

button_tab = Panel(child=button_plot, title='Missions')
inputs = Tabs(tabs=[ button_tab]) 

# Set up layouts and add to document
curdoc().add_root(row(children=[inputs ])) 
