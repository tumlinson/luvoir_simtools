import numpy as np
from bokeh.io import curdoc
from bokeh.layouts import column, row, widgetbox
from bokeh.models import ColumnDataSource, HoverTool, Range1d, BoxSelectTool, Segment, Square
from bokeh.models.widgets import Slider
from bokeh.plotting import Figure


relation_properties = ColumnDataSource(data=dict(power_law_slope=[0.15], arbitrary_normalization=[2.2])) 

# here is a CDS for the shutter positions. Just made up for now.
cluster_masses = np.array([5.5, 5.1, 2.6, 7.2, 6.1, 5.5, 5.4, 3.4, 4.3, 4.1, 3.5, 3.6, 3.7, 4.9, 4.8, \
    5., 4.9, 4.8, 4.1, 4.3, 4.2, 4.0, 3.3, 2.3, 3.6, 3.3, 3.2, 1.2, 6.1, 6.7, 3.9, 4.2])
cluster_xcoords = 60. * np.random.rand(np.size(cluster_masses)) - 30.
cluster_ycoords = 60. * np.random.rand(np.size(cluster_masses)) - 30.
scatter_term = 2.0 * np.random.rand(np.size(cluster_masses)) - 1.0
cluster_vmax = (10. ** (cluster_masses + scatter_term) / 1000.) ** relation_properties.data['power_law_slope'] * 300.
vmax_up_error =  cluster_vmax + 300. 
vmax_down_error = cluster_vmax - 300. 

shutter_positions = ColumnDataSource(
    data=dict(x=cluster_xcoords, y=cluster_ycoords, vmax=cluster_vmax, mass=cluster_masses, scatter=scatter_term, \
               vmax_up_error=vmax_up_error, vmax_down_error=vmax_down_error))



# Set up plot
box_select = BoxSelectTool()
plot1 = Figure(plot_height=500, plot_width=770, x_axis_type=None, y_axis_type=None,
               tools=["pan,reset,resize,tap,box_zoom,wheel_zoom,save", box_select],
               x_range=[-75, 75], y_range=[-50, 50], toolbar_location='left')
plot1.image_url(url=["http://www.jt-astro.science/hs-2014-04-a-print.jpg"], x=[-75], y=[50], w=150, h=100)
#plot1.image_url(url=["http://farm9.staticflickr.com/8238/8416833561_a5e096d251_o.jpg"], x=[-50], y=[50], w=100, h=100)
plot1.x_range = Range1d(-75, 75, bounds=(-75, 75))
plot1.y_range = Range1d(-50, 50, bounds=(-50, 50))
shutters = plot1.square('x', 'y', source=shutter_positions,
                        fill_color='yellow', fill_alpha=0.2, line_color=None, size=20, name="my_shutters")
shutters.selection_glyph = Square(fill_alpha=0.5, fill_color="green", line_color='green', line_width=3)
shutters.nonselection_glyph = Square(fill_alpha=0.2, fill_color="yellow", line_color=None)

hover = HoverTool(renderers=[shutters], point_policy="snap_to_data",
                  tooltips="""
        <div>
            <div>
                <span style="font-size: 15px; font-weight: bold; color: #696">Mass = @mass  Msun</span>
            </div>
            <div>
                <span style="font-size: 15px; font-weight: bold; color: #696">Vmax = </span>
                <span style="font-size: 15px; font-weight: bold; color: #696;">@vmax km / s</span>
            </div>
        </div>
        """
                  )
plot1.add_tools(hover)

# this is a grey square grid for convenience at reading coordinates 
for xx in np.arange(17) * 10. - 80:
    print xx
    plot1.line([xx, xx], [-50, 50], line_width=1, line_color='grey')
    plot1.line([-75, 75], [xx, xx], line_width=1, line_color='grey')

# set up the cluster vmax vs. mass plot
plot2 = Figure(plot_height=400, plot_width=450, tools="pan,reset,wheel_zoom,hover,save", outline_line_color='black',
               x_range=[2, 7], y_range=[80, 1500], y_axis_type='log', toolbar_location='right',
               title=' Outflow Properties')
plot2.background_fill_color = "beige"
plot2.title.text_font_size = '14pt'
plot2.title.align = 'center'
plot2.background_fill_alpha = 0.5
plot2.yaxis.axis_label = 'Max Outflow Velocity [km/s]'
plot2.xaxis.axis_label = 'log(Cluster Mass)'
plot2.xaxis.axis_line_color = 'black'
plot2.yaxis.axis_line_color = 'black'
plot2.border_fill_color = "white"
plot2.min_border_left = 100


cluster_points = plot2.square('mass', 'vmax', source=shutter_positions, size=15, color='grey', line_color=None,
                              fill_alpha=0.1)
cluster_points.selection_glyph = Square(fill_alpha=0.5, fill_color="green", line_color='green', line_width=3)
cluster_points.nonselection_glyph = Square(fill_alpha=0.1, fill_color="grey", line_color=None)
cluster_errors = plot2.segment('mass', 'vmax_up_error', 'mass', 'vmax_down_error', source=shutter_positions, line_width=2, line_color='grey', line_alpha=0.1) 
cluster_errors.selection_glyph = Segment(line_alpha=0.5, line_color='green', line_width=3) 
cluster_errors.nonselection_glyph = Segment(line_alpha=0.1, line_color='grey', line_width=1) 


# Set up control widgets
aperture = Slider(title="Aperture (meters)", value=12., start=4., end=20.0, step=1.0)
exposure = Slider(title="Exposure Time (hr)", value=1, start=1.0, end=10., step=1.0)

power_law_slider = Slider(title="Power Law Slope", value=0.15, start=0.0, end=1., step=0.05)


def update_data(attrname, old, new):  # callback for slider moves

    a = aperture.value  # Get the current slider values
    c = exposure.value
    print 'APERTURE AND EXPOSURE SLIDERS ARE NOT WORKING YET FOR THIS TOOL'

def shutter_updater(attr, old, new):  # callback for shutter selection
    indexes = np.array(new['1d']['indices'], dtype='int')
    masses = np.array(shutter_positions.data['mass'])

def power_law_updater(attr, old, new): 
    print 'want to change the power law to', power_law_slider.value 
    relation_properties.data['power_law_slope'] = power_law_slider.value 
    cluster_masses = np.array([5.5, 5.1, 2.6, 7.2, 6.1, 5.5, 5.4, 3.4, 4.3, 4.1, 3.5, 3.6, 3.7, 4.9, 4.8, \
        5., 4.9, 4.8, 4.1, 4.3, 4.2, 4.0, 3.3, 2.3, 3.6, 3.3, 3.2, 1.2, 6.1, 6.7, 3.9, 4.2])
    scatter_term = 2.0 * np.random.rand(np.size(cluster_masses)) - 1.0
    cluster_vmax = (10. ** (cluster_masses + shutter_positions.data['scatter'] ) / 1000.) ** relation_properties.data['power_law_slope'] * 300.
    vmax_up_error =  cluster_vmax + 300. / exposure.value**0.5 / (aperture.value / 12.)
    vmax_down_error = cluster_vmax - 300. / exposure.value**0.5 / (aperture.value / 12.)
    
    shutter_positions.data['vmax'] = cluster_vmax 
    shutter_positions.data['vmax_up_error'] = vmax_up_error 
    shutter_positions.data['vmax_down_error'] = vmax_down_error
    print shutter_positions.data['vmax_up_error'], shutter_positions.data['vmax_down_error'] 


# iterate on changes to parameters
for w in [aperture, exposure]:
    w.on_change('value', update_data)

for s in [aperture, exposure, power_law_slider]: 
    s.on_change('value', power_law_updater)

# this triggers the "shutter_updater" function when a shutter is selected
shutters.data_source.on_change('selected', shutter_updater)

layout = row(plot1, column(widgetbox(children=[aperture, exposure], width=500, sizing_mode='scale_width'), plot2, widgetbox(power_law_slider,width=500)))
curdoc().add_root(layout)




