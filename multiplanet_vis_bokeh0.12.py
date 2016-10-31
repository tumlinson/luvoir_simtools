''' 
this is run by typing "bokeh serve --show myapp.py" on the command line 
'''
import numpy as np
import math 

from astropy.table import Table 
import copy  

from bokeh.io import output_file, gridplot 
from bokeh.plotting import Figure
from bokeh.resources import CDN
from bokeh.client import push_session
from bokeh.embed import components, file_html
from bokeh.models import ColumnDataSource, HoverTool, Range1d, Square, Circle, LabelSet, FixedTicker 
from bokeh.layouts import Column, Row, WidgetBox
from bokeh.models.glyphs import Text 
from bokeh.models.widgets import Slider, TextInput
from bokeh.io import hplot, vplot, curdoc
from bokeh.models.callbacks import CustomJS


targets = Table.read('data/stark_multiplanet/run_4.0_1.00E-10_3.6_0.1_3.0.fits')  
col = copy.deepcopy(targets['TYPE'][0]) 
col[:] = 'black' 
col[np.where(targets['COMPLETENESS'][0] > 0.2*0.1)] = 'red' 
col[np.where(targets['COMPLETENESS'][0] > 0.5*0.1)] = 'yellow' 
col[np.where(targets['COMPLETENESS'][0] > 0.8*0.1)] = 'lightgreen' 

totyield = np.sum(targets['COMPLETENESS'][0] * 0.1) 

# x0,y0 = original positons, will not be changed 
# x,y = positions that will be modified to hide C = 0 stars in view 
star_points = ColumnDataSource(data=dict(x0 = targets['X'][0], \
                                         y0 = targets['Y'][0], \
                                         x  = targets['X'][0], \
                                         y  = targets['Y'][0], \
                                         r  = targets['DISTANCE'][0], \
                                         stype=targets['TYPE'][0], \
                                         hip=targets['HIP'][0], \
                                         color=col, \
                                         complete=targets['COMPLETENESS'][0], \
                                         complete0=targets['COMPLETE0'][0], \
                                         complete1=targets['COMPLETE1'][0], \
                                         complete2=targets['COMPLETE2'][0], \
                                         complete3=targets['COMPLETE3'][0], \
                                         complete4=targets['COMPLETE4'][0], \
                                         complete5=targets['COMPLETE5'][0], \
                                         complete6=targets['COMPLETE6'][0], \
                                         complete7=targets['COMPLETE7'][0], \
                                         complete8=targets['COMPLETE8'][0]  \
                                         )) # end of the stars CDS 


black_points = [star_points.data['color'] == 'black'] 
star_points.data['x'][black_points] += 2000. 


rad_circles = ColumnDataSource(data=dict(x=np.array([0., 0., 0., 0.]), \
                  y=np.array([0., 0., 0., 0.]), cfrac=[0., 0., 0., 0.], \
                  fillcolor=['black', 'black','black','0.342']))

# Set up plot
plot1 = Figure(plot_height=800, plot_width=800, x_axis_type = None, y_axis_type = None,
              tools="pan,reset,resize,save,tap,box_zoom,wheel_zoom", outline_line_color='black', 
              x_range=[-50, 50], y_range=[-50, 50], toolbar_location='right')

hover = HoverTool(names=["star_points_to_hover"], mode='mouse', # point_policy="snap_to_data",
     tooltips = """ 
        <div>
            <div>
                <img
                    src="http://www.stsci.edu/~tumlinso/earth_spec.jpg" height="150" alt="@imgs" width="271"
                    style="float: left; margin: 0px 15px 15px 0px;"
                    border="2"
                ></img>
            </div>
            <div>
                <span style="font-size: 20px; font-weight: bold; color: #696">HIP</span>
                <span style="font-size: 20px; font-weight: bold; color: #696">@hip</span>
            </div>
            <div>
                <span style="font-size: 20px; font-weight: bold; color: #696">@stype</span>
                <span style="font-size: 20px; font-weight: bold; color: #696">type</span>
            </div>
            <div>
                <span style="font-size: 20px; font-weight: bold; color: #696">D = </span>
                <span style="font-size: 20px; font-weight: bold; color: #696;">@r</span>
                <span style="font-size: 20px; font-weight: bold; color: #696;"> pc</span>
            </div>
            <div>
                <span style="font-size: 20px; font-weight: bold; color: #696">C = </span>
                <span style="font-size: 20px; font-weight: bold; color: #696;">@complete</span>
            </div>
        </div>
        """
    )
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
plot1.min_border_left = 80

# main glyphs for planet circles  
star_syms = plot1.circle('x', 'y', source=star_points, name="star_points_to_hover", \
      fill_color='color', line_color='color', radius=0.5, line_alpha=0.5, fill_alpha=0.7)
star_syms.selection_glyph = Circle(fill_alpha=0.8, fill_color="purple", radius=1.5, line_color='purple', line_width=3)

plot1.text(0.95*0.707*np.array([10., 20., 30., 40.]), 0.707*np.array([10., 20., 30., 40.]), \
     text=['10 pc', '20 pc', '30 pc', '40 pc'], text_color="white", text_font_style='bold', text_font_size='12pt', text_alpha=0.8) 
plot1.text([48.5], [47], ['Chance Of Detecting'], text_color="white", text_align="right", text_alpha=1.0) 
plot1.text([48.5], [44.5], ['an Earth Twin if Present'], text_color="white", text_align="right", text_alpha=1.0) 
plot1.text([48.5], [44.5], ['___________________'], text_color="white", text_align="right", text_alpha=1.0) 
plot1.text(np.array([48.5]), np.array([41.5]), ["80-100%"], text_color='lightgreen', text_align="right") 
plot1.text(np.array([48.5]), np.array([41.5-1*2.4]), ["50-80%"], text_color='yellow', text_align="right") 
plot1.text(np.array([48.5]), np.array([41.5-2*2.4]), ["20-50%"], text_color='red', text_align="right") 
plot1.text(np.array([48.5]), np.array([41.5-3*2.4]), ["Not Observed"], text_color='black', text_align="right") 
plot1.circle([0], [0], radius=0.1, fill_alpha=1.0, line_color='white', fill_color='white') 
plot1.circle([0], [0], radius=0.5, fill_alpha=0.0, line_color='white') 

sym = plot1.circle('x', 'y', source=rad_circles, fill_color='fillcolor', line_color='white', 
           line_width=4, radius=[40,30,20,10], line_alpha=0.8, fill_alpha=0.0) 
sym.glyph.line_dash = [6, 6]



# second plot, the "table" of Yields 
plot2 = Figure(plot_height=400, plot_width=450, tools=" ", outline_line_color='black', \
              x_range=[0, 4], y_range=[0, 4], toolbar_location='left', x_axis_type=None, y_axis_type=None, \
              title='                        Multiplanet Yields') 
plot2.text([2.0], [3.0], ['Earth-like'], text_color="black", text_align="center", text_alpha=1.0) 
plot2.text([2.0], [3.0], ['____________________________________________'], text_color="black", text_align="center", text_alpha=1.0) 
plot2.text([2.0], [2.0], ['Neptune-like'], text_color="black", text_align="center", text_alpha=1.0) 
plot2.text([2.0], [2.0], ['____________________________________________'], text_color="black", text_align="center", text_alpha=1.0) 
plot2.text([2.0], [1.0], ['Jupiter-like'], text_color="black", text_align="center", text_alpha=1.0) 
plot2.text([2.0], [1.0], ['____________________________________________'], text_color="black", text_align="center", text_alpha=1.0) 
plot2.text([0.5], [3.4], ['Cool'], text_color="black", text_align="center", text_alpha=1.0) 
plot2.text([2.0], [3.4], ['Warm'], text_color="black", text_align="center", text_alpha=1.0) 
plot2.text([3.5], [3.4], ['Hot'], text_color="black", text_align="center", text_alpha=1.0) 
plot2.title.text_font_size = '14pt' 
plot2.background_fill_color = "white"
plot2.background_fill_alpha = 0.5 
plot2.yaxis.axis_label = ' ' 
plot2.xaxis.axis_label = ' ' 
plot2.xaxis.axis_line_width = 0
plot2.yaxis.axis_line_width = 0 
plot2.xaxis.axis_line_color = 'white' 
plot2.yaxis.axis_line_color = 'white' 
plot2.border_fill_color = "white"
plot2.min_border_left = 0


# this will place labels in the small plot for the *selected star* - not implemented yet 
star_yield_label = ColumnDataSource(data=dict(labels=["0","0","0","0","0","0","0","0","0"], \
                                         xvals =[0.5,2.0,3.5,0.5,2.,3.5,0.5,2.,3.5], yvals =[2.7,2.7,2.7,1.7,1.7,1.7,0.7,0.7,0.7,])) 
plot2.add_glyph(star_yield_label, Text(x="xvals", y="yvals", text="labels", text_align='center', text_font_size='14pt'))

total_yield_label = ColumnDataSource(data=dict(labels=["0","0","0","0","0","0","0","0","0"], \
                                         xvals =[0.5,2.0,3.5,0.5,2.,3.5,0.5,2.,3.5], yvals =[2.3,2.3,2.3,1.3,1.3,1.3,0.3,0.3,0.3,])) 
plot2.add_glyph(total_yield_label, Text(x="xvals", y="yvals", text="labels", text_align='center', text_color='red', text_font_size='16pt'))


def update_data(attrname, old, new):

    a = aperture.value 
    c = contrast.value 
    i = iwa.value 

    print 'APERTURE A = ', a, ' CONTRAST C = ', c, ' IWA I = ', i 
    apertures = {'4.0':'4.0','4':'4.0','6':'6.0','6.0':'6.0','8':'8.0','8.0':'8.0',\
                 '10':'10.0','10.0':'10.0','12':'12.0','12.0':'12.0','14':'14.0',\
                 '14.0':'14.0','16':'16.0'} 
    contrasts = {'-11':'1.00E-11','-10':'1.00E-10','-9':'1.00E-09'} 
    filename = 'data/stark_multiplanet/'+'run_'+apertures[str(a)]+'_'+contrasts[str(c)]+'_3.6_0.1_3.0.fits' 
    targets = Table.read(filename) 
    star_points.data['complete'] = np.array(targets['COMPLETENESS'][0]) 

    star_yield_label.data['labels'] = [str(targets['COMPLETE0'][0][832])[0:5], \
                                  str(targets['COMPLETE1'][0][832])[0:5], \
                                  str(targets['COMPLETE2'][0][832])[0:5], \
                                  str(targets['COMPLETE3'][0][832])[0:5], \
                                  str(targets['COMPLETE4'][0][832])[0:5], \
                                  str(targets['COMPLETE5'][0][832])[0:5], \
                                  str(targets['COMPLETE6'][0][832])[0:5], \
                                  str(targets['COMPLETE7'][0][832])[0:5], \
                                  str(targets['COMPLETE8'][0][832])[0:5]] 

    total_yield_label.data['labels'] = [str(np.sum(targets['COMPLETE0'][0][:]))[0:5], \
                                        str(np.sum(targets['COMPLETE1'][0][:]))[0:5], \
                                        str(np.sum(targets['COMPLETE2'][0][:]))[0:5], \
                                        str(np.sum(targets['COMPLETE3'][0][:]))[0:5], \
                                        str(np.sum(targets['COMPLETE4'][0][:]))[0:5], \
                                        str(np.sum(targets['COMPLETE5'][0][:]))[0:5], \
                                        str(np.sum(targets['COMPLETE6'][0][:]))[0:5], \
                                        str(np.sum(targets['COMPLETE7'][0][:]))[0:5], \
                                        str(np.sum(targets['COMPLETE8'][0][:]))[0:5]] 
 
    # colors corresponding to yields are updated here 
    col = copy.deepcopy(targets['TYPE'][0]) 
    col[:] = 'black' 
    col[np.where(targets['COMPLETENESS'][0] < 0.2*0.1)] = 'black' 
    col[np.where(targets['COMPLETENESS'][0] > 0.2*0.1)] = 'red' 
    col[np.where(targets['COMPLETENESS'][0] > 0.5*0.1)] = 'yellow' 
    col[np.where(targets['COMPLETENESS'][0] > 0.8*0.1)] = 'lightgreen' 
    star_points.data['color'] = col

    # reset the positions and hide the low completion stars by shifting their X 
    star_points.data['x'] = star_points.data['x0'] 
    star_points.data['y'] = star_points.data['y0'] 
    x = copy.deepcopy(targets['X'][0]) 
    x[col == 'black'] = x[col == 'black'] + 2000. 
    star_points.data['x'] = x 
    
    yield_now = np.sum(targets['COMPLETENESS'][0]) * 0.1 
    #rect_points.data['top'] = np.array([yield_now,a,a])/2. - 50. 
    #rect_points.data['strbag'] = str(np.sum(np.array(targets['COMPLETENESS'][0]))) 

    star_points.data['COMPLETE0'] = np.array(targets['COMPLETE0'][0]) 
    star_points.data['COMPLETE1'] = np.array(targets['COMPLETE1'][0]) 
    star_points.data['COMPLETE2'] = np.array(targets['COMPLETE2'][0]) 
    star_points.data['COMPLETE3'] = np.array(targets['COMPLETE3'][0]) 
    star_points.data['COMPLETE4'] = np.array(targets['COMPLETE4'][0]) 
    star_points.data['COMPLETE5'] = np.array(targets['COMPLETE5'][0]) 
    star_points.data['COMPLETE6'] = np.array(targets['COMPLETE6'][0]) 
    star_points.data['COMPLETE7'] = np.array(targets['COMPLETE7'][0]) 
    star_points.data['COMPLETE8'] = np.array(targets['COMPLETE8'][0]) 

source = ColumnDataSource(data=dict(value=[]))
source.on_change('data', update_data)
    
# Set up widgets
aperture= Slider(title="Aperture (meters)", value=4., start=4., end=16.0, step=2.0, callback_policy='mouseup')
aperture.callback = CustomJS(args=dict(source=source), code="""
    source.data = { value: [cb_obj.value] }
""")
contrast = Slider(title="Log (Contrast)", value=-10, start=-11.0, end=-9, step=1.0, callback_policy='mouseup')
contrast.callback = CustomJS(args=dict(source=source), code="""
    source.data = { value: [cb_obj.value] }
""")
iwa      = Slider(title="Inner Working Angle (l/D)", value=1.5, start=1.5, end=4.0, step=0.5, callback_policy='mouseup')
iwa.callback = CustomJS(args=dict(source=source), code="""
    source.data = { value: [cb_obj.value] }
""")
 

# iterate on changes to parameters 
#for w in [aperture, contrast]: 
#    w.on_change('value', update_data)
 
# Set up layouts and add to document
inputs = Column(children=[aperture, contrast, plot2]) 
curdoc().add_root(Row(children=[inputs, plot1], width=1800))
curdoc().add_root(source) 

