''' 
this is run by typing "bokeh serve --show myapp.py" on the command line 
'''
import numpy as np
import math 

from astropy.table import Table 
import copy  
import os 

from bokeh.io import output_file, gridplot 
from bokeh.plotting import Figure
from bokeh.resources import CDN
from bokeh.client import push_session
from bokeh.embed import components, file_html
from bokeh.models import ColumnDataSource, HoverTool, Range1d, Square, Circle, LabelSet, FixedTicker, TapTool 
from bokeh.layouts import Column, Row, WidgetBox
from bokeh.models.glyphs import Text 
from bokeh.models.widgets import Slider, TextInput
from bokeh.io import hplot, vplot, curdoc
from bokeh.models.callbacks import CustomJS

cwd = os.getenv('LUVOIR_SIMTOOLS_DIR')

# obtain the yield table for the nominal parameter set
targets = Table.read(cwd+'multiplanet_vis/data/stark_multiplanet/run_4.0_1.00E-10_3.6_0.1_3.0.fits')  
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
                                         complete2=targets['COMPLETE2'][0]*targets['MP_ETA'][0][1], \
                                         complete3=targets['COMPLETE3'][0], \
                                         complete4=targets['COMPLETE4'][0], \
                                         complete5=targets['COMPLETE5'][0]*targets['MP_ETA'][0][4], \
                                         complete6=targets['COMPLETE6'][0], \
                                         complete7=targets['COMPLETE7'][0], \
                                         complete8=targets['COMPLETE8'][0]*targets['MP_ETA'][0][7]  \
                                         )) # end of the stars CDS 
black_points = [star_points.data['color'] == 'black'] 
star_points.data['x'][black_points] += 2000. 	# this line shifts the black points with no yield off the plot 



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
### THIS IS THE HOVER HELP FOR THE MAIN WINDOW 
hover_help = HoverTool(names=["quickhelp_to_hover"], mode='mouse', 
     tooltips = """ 
            <div>
                <span style="font-size: 16px; font-weight: normal; color: #000">
                This tool visualizes the results of detailed exoplanet mission <br> 
                yield simulations described in Stark et al. (2014), ApJ, 795, 122 <br> 
                Stark et al. (2015), ApJ, 808, 149. The python/bokeh visualization <br> 
		is by <a href='http://jt-astro.science'>Jason Tumlinson</a>. <br> <br> 
           </div>
           <div>
                <span style="font-size: 16px; font-weight: normal; color: #000">
                For this analysis, the fraction of stars with exoEarth <br> 
                candidates (Eta_Earth) is assumed to be 10%. The planets <br>
                are observed over 1 year of total exposure time using <br> 
                high-contrast optical imaging with a coronagraph. At least <br> 
                one imaging observation of every star is performed to find <br>
                the exoEarth candidates (blind search). For every detected <br>
                planet, a partial spectroscopic characterization is executed. <br>
                The telescope aperture and coronagraph contrast can be varied <br>
                with the slider bars. The real host stars observed are shown <br>
                with colored dots in the main plot, with the Sun at the center <br>
                (hovering the cursor over a dot will reveal the star name<br>
                and parameters). The color of the dot indicates the chance <br>
                of detecting an exoEarth around that star if it is present.
                </span>
        </div>
 
        """
    )
plot1.add_tools(hover_help) 
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

def SelectCallback(attrname, old, new): 
    inds = np.array(new['1d']['indices'])[0] # this miraculously obtains the index of the slected star within the star_syms CDS 
    print inds, star_points.data['complete0'][inds], str(star_points.data['complete0'][inds])[0:6] 
    star_yield_label.data['labels'] = [str(star_points.data['complete0'][inds])[0:6], \
 			               str(star_points.data['complete1'][inds])[0:6], \
 			               str(star_points.data['complete2'][inds])[0:6], \
 			               str(star_points.data['complete3'][inds])[0:6], \
 			               str(star_points.data['complete4'][inds])[0:6], \
 			               str(star_points.data['complete5'][inds])[0:6], \
 			               str(star_points.data['complete6'][inds])[0:6], \
 			               str(star_points.data['complete7'][inds])[0:6], \
 			               str(star_points.data['complete8'][inds])[0:6]] 

# main glyphs for planet circles  
star_syms = plot1.circle('x', 'y', source=star_points, name="star_points_to_hover", \
      fill_color='color', line_color='color', radius=0.5, line_alpha=0.5, fill_alpha=0.7)
star_syms.selection_glyph = Circle(fill_alpha=0.8, fill_color="orange", radius=1.5, line_color='purple', line_width=3)
star_syms.data_source.on_change('selected', SelectCallback)
#taptool = plot1.select(type=TapTool)
#taptool.callback = FuncFunc() 

quickhelp_source = ColumnDataSource(data=dict(x=np.array([44.0]), y=np.array([32.]), text=['Help']))
help_glyph = plot1.circle('x', 'y', color='black', source=quickhelp_source, radius=4, name="quickhelp_to_hover") 
plot1.text([48.5], [30], ['Help'], text_color='orange', text_font_size='18pt', text_align="right") 

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

sym = plot1.circle(np.array([0., 0., 0., 0.]), np.array([0., 0., 0., 0.]), fill_color='black', line_color='white', 
           line_width=4, radius=[40,30,20,10], line_alpha=0.8, fill_alpha=0.0) 
sym.glyph.line_dash = [6, 6]

# second plot, the bar chart of yields
plot3 = Figure(plot_height=400, plot_width=480, tools="reset,save,tap",
               outline_line_color='black', \
              x_range=[-0.1, 3], y_range=[0, 100], toolbar_location='above', x_axis_type = None, \
              title='Multiplanet Yields') 
plot3.title.text_font_size = '14pt'
plot3.background_fill_color = "white"
plot3.background_fill_alpha = 1.0
plot3.yaxis.axis_label = 'X'
plot3.xaxis.axis_label = 'Y'
plot3.xaxis.axis_line_width = 2
plot3.yaxis.axis_line_width = 2
plot3.xaxis.axis_line_color = 'black'
plot3.yaxis.axis_line_color = 'black'
plot3.border_fill_color = "white"
plot3.min_border_left = 0
plot3.image_url(url=["http://jt-astro.science/planets.jpg"], x=[-0.2], y=[105], w=[3.2], h=[105])

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
                                        mass=['Earths','Earths','Earths','Neptunes','Neptunes','Neptunes','Jupiters','Jupiters','Jupiters'], 
                                        labels=["0","0","0","0","0","0","0","0","0"], \
                                        xvals =[1.5,2.5,3.5,1.5,2.5,3.5,1.5,2.5,3.5], \
                                        yvals =[2.5,2.5,2.5,1.5,1.5,1.5,0.5,0.5,0.5,]))
plot3.quad(top='yields', bottom=0., left='left', right='right', \
           source=total_yield_label, color='color', fill_alpha=0.9, line_alpha=1., name='total_yield_label_hover')
plot3.text('left', 'yields', 'labels', 0., 20, -3, text_align='center', source=total_yield_label, text_color='black')

yield_hover = HoverTool(names=["total_yield_label_hover"], mode='mouse', # point_policy="snap_to_data",
     tooltips = """ 
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
plot3.add_tools(yield_hover) 

def update_data(attrname, old, new):

    a = aperture.value 
    c = contrast.value 
    i = iwa.value 

    print 'APERTURE A = ', a, ' CONTRAST C = ', c, ' IWA I = ', i 
    apertures = {'4.0':'4.0','4':'4.0','6':'6.0','6.0':'6.0','8':'8.0','8.0':'8.0',\
                 '10':'10.0','10.0':'10.0','12':'12.0','12.0':'12.0','14':'14.0',\
                 '14.0':'14.0','16':'16.0'} 
    contrasts = {'-11':'1.00E-11','-10':'1.00E-10','-9':'1.00E-09'} 
    filename = cwd+'multiplanet_vis/data/stark_multiplanet/'+'run_'+apertures[str(a)]+'_'+contrasts[str(c)]+'_3.6_0.1_3.0.fits' 
    targets = Table.read(filename) 
    star_points.data['complete'] = np.array(targets['COMPLETENESS'][0]) 

    star_yield_label.data['yields'] = [targets['COMPLETE0'][0][1410], \
                                  targets['COMPLETE1'][0][1410], \
                                  targets['MP_ETA'][0][1] * targets['COMPLETE2'][0][1410], \
                                  targets['COMPLETE3'][0][1410], \
                                  targets['COMPLETE4'][0][1410], \
                                  targets['MP_ETA'][0][4] * targets['COMPLETE5'][0][1410], \
                                  targets['COMPLETE6'][0][1410], \
                                  targets['COMPLETE7'][0][1410], \
                                  targets['MP_ETA'][0][7] * targets['COMPLETE8'][0][1410]]
    star_yield_label.data['labels'] = [str(targets['COMPLETE0'][0][1410])[0:5], \
                                       str(targets['COMPLETE1'][0][1410])[0:5], \
                                       str(targets['MP_ETA'][0][1] * targets['COMPLETE2'][0][1410])[0:5], \
                                       str(targets['COMPLETE3'][0][1410])[0:5], \
                                       str(targets['COMPLETE4'][0][1410])[0:5], \
                                       str(targets['MP_ETA'][0][4] * targets['COMPLETE5'][0][1410])[0:5], \
                                       str(targets['COMPLETE6'][0][1410])[0:5], \
                                       str(targets['COMPLETE7'][0][1410])[0:5], \
                                       str(targets['MP_ETA'][0][7] * targets['COMPLETE8'][0][1410])[0:5]]
    total_yield_label.data['yields'] = [np.sum(targets['COMPLETE0'][0][:]), \
                                        np.sum(targets['COMPLETE1'][0][:]), \
                                        np.sum(targets['MP_ETA'][0][1] * targets['COMPLETE2'][0][:]), \
                                        np.sum(targets['COMPLETE3'][0][:]), \
                                        np.sum(targets['COMPLETE4'][0][:]), \
                                        np.sum(targets['MP_ETA'][0][4] * targets['COMPLETE5'][0][:]), \
                                        np.sum(targets['COMPLETE6'][0][:]), \
                                        np.sum(targets['COMPLETE7'][0][:]), \
                                        np.sum(targets['MP_ETA'][0][7] * targets['COMPLETE8'][0][:])]
    print 'Total Yields', total_yield_label.data['yields']
    total_yield_label.data['labels'] = [str(int(np.sum(targets['COMPLETE0'][0][:]))), \
                                        str(int(np.sum(targets['COMPLETE1'][0][:]))), \
                                        str(int(targets['MP_ETA'][0][1]*np.sum(targets['COMPLETE2'][0][:]))), \
                                        str(int(np.sum(targets['COMPLETE3'][0][:]))), \
                                        str(int(np.sum(targets['COMPLETE4'][0][:]))), \
                                        str(int(targets['MP_ETA'][0][4]*np.sum(targets['COMPLETE5'][0][:]))), \
                                        str(int(np.sum(targets['COMPLETE6'][0][:]))), \
                                        str(int(np.sum(targets['COMPLETE7'][0][:]))), \
                                        str(int(targets['MP_ETA'][0][7]*np.sum(targets['COMPLETE8'][0][:])))]

    print 'MP_ETA', targets['MP_ETA'][0]
 
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

# Set up layouts and add to document
inputs = Column(children=[aperture, contrast, plot3])
curdoc().add_root(Row(children=[inputs, plot1], width=1800))
curdoc().add_root(source) 

