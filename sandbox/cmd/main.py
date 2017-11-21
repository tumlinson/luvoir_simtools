from __future__ import absolute_import, print_function, division
import argparse
from os import path
import yaml
import uuid
from collections import OrderedDict
import pandas as pd
from bokeh.server.server import Server
from bokeh.application import Application
from bokeh.application.handlers import FunctionHandler
from bokeh.plotting import Figure
from bokeh.models import ColumnDataSource,Range1d, ImageSource, TMSTileSource, WMTSTileSource, TileRenderer, DynamicImageRenderer, Row, Column 
from bokeh.models import Select, Slider, Panel, Tabs 
import datashader as ds
import datashader.transfer_functions as tf
import numpy as np 
from colorcet import palette
from datashader.bokeh_ext import HoverLayer, create_categorical_legend, create_ramp_legend
from datashader.utils import hold
from tornado.ioloop import IOLoop
from tornado.web import RequestHandler
from webargs import fields
from webargs.tornadoparser import use_args
from astropy.table import Table 

# http request arguments for datashading HTTP request
ds_args = {
    'width': fields.Int(missing=800),
    'height': fields.Int(missing=600),
    'select': fields.Str(missing="") 
}

def odict_to_front(odict,key):
    """Given an OrderedDict, move the item with the given key to the front."""
    front_item = [(key,odict[key])]
    other_items = [(k,v) for k,v in odict.items() if k is not key]
    return OrderedDict(front_item+other_items)

class GetDataset(RequestHandler):

    """Handles http requests for datashading."""
    @use_args(ds_args)

    def get(self, args):

        # parse args
        print("args to get :", args) # these numbers accurately reflect range that is actually displayed, so where do they come from ? ? 
        #WHAT CALLED THIS FUNCTION? 
        #Args:  {'width': 271, 'select': u'-5.056915906244413,-4.831928288268559,5.056915906244413,14.831928288268559', 'height': 527}
        selection = args['select'].strip(',').split(',')
        print("Args: ", args) 
        xmin, ymin, xmax, ymax = map(float, selection)
        self.model.map_extent = [xmin, ymin, xmax, ymax]

        glyph = self.model.glyph.get(str(self.model.field), 'points') # telling DS to use points - not sure about options 

        # create image
        self.model.agg = self.model.create_aggregate(args['width'],
                                                     args['height'],
                                                     (xmin, xmax),
                                                     (ymin, ymax),
 					             self.model.age, ##### THIS IS IT!! ADDING A CONTROL PARAMTER HERE 
								     ##### CAUSED THE SOURCE TO UPDATE AND THE IMAGE TO RENDER ON CHANGE
                                                     self.model.aperture,
                                                     self.model.field,
                                                     self.model.active_axes['xaxis'],
                                                     self.model.active_axes['yaxis'],
                                                     self.model.agg_function_name, glyph)
        pix = self.model.render_image()

        def update_plots():
            return 

        server.get_sessions('/')[0].with_document_locked(update_plots)
        # serialize to image
        img_io = pix.to_bytesio()
        self.write(img_io.getvalue())
        self.set_header("Content-type", "image/png")



class AppState(object):
    """Simple value object to hold app state"""

    def __init__(self, outofcore): 

        self.load_config_file('/Users/tumlinson/Dropbox/LUVOIR/SYOTools/luvoir_simtools/sandbox/cmd/cmd.yml') 
        self.plot_height = 600
        self.plot_width = 350

        self.aperture = 10. 
        self.age = 9.0 
        self.distance = 100. 

        self.aggregate_functions = OrderedDict()
        self.aggregate_functions['Mean'] = ds.mean
        self.aggregate_functions['Count'] = ds.count
        self.aggregate_functions['Sum'] = ds.sum
        self.aggregate_functions['Min'] = ds.min
        self.aggregate_functions['Max'] = ds.max
        self.agg_function_name = list(self.aggregate_functions.keys())[0] # initial definition - no action 

        self.transfer_functions = OrderedDict()   # transfer function configuration
        self.transfer_functions['Histogram Equalization'] = 'eq_hist'
        self.transfer_functions['Linear'] = 'linear'
        self.transfer_functions['Log'] = 'log'
        self.transfer_function = list(self.transfer_functions.values())[0]

        # dynamic image configuration
        self.service_url = 'http://{host}:{port}/datashader?'
        self.service_url += 'height={HEIGHT}&'
        self.service_url += 'width={WIDTH}&'
        self.service_url += 'select={XMIN},{YMIN},{XMAX},{YMAX}&'
        self.service_url += 'cachebust={cachebust}'

        self.shader_url_vars = {}
        self.shader_url_vars['host'] = 'localhost'
        self.shader_url_vars['port'] = 5006 
        self.shader_url_vars['cachebust'] = str(uuid.uuid4())

        self.load_datasets(False) # call to load_datasets to obtain desired data file (fits or csv) 
        
        self.spread_size = 1    # spreading

        # color ramps - these are drawn from colorcet palettes and could be adapted 
        default_palette = "blues"
        named_palettes = {k:p for k,p in palette.items() if not '_' in k}
        sorted_palettes = OrderedDict(sorted(named_palettes.items()))
        self.color_ramps = odict_to_front(sorted_palettes,default_palette)
        self.color_ramp  = palette[default_palette]

        self.agg = None

    def load_config_file(self, config_path):
        '''load and parse yaml config file'''

        if not path.exists(config_path):
            raise IOError('Unable to find config file "{}"'.format(config_path))

        self.config_path = path.abspath(config_path)

        with open(config_path) as f:
            self.config = yaml.load(f.read())

        # parse plots
        self.axes = OrderedDict()
        for p in self.config['axes']:
            self.axes[p['name']] = p
        self.active_axes = list(self.axes.values())[0]

        # parse initial extent
        extent = self.active_axes['initial_extent']
        self.map_extent = [extent['xmin'], extent['ymin'],
                           extent['xmax'], extent['ymax']]

        self.xtitle = self.active_axes['xtitle']  
        self.ytitle = self.active_axes['ytitle']  

        # parse summary field
        self.fields = OrderedDict()
        self.colormaps = OrderedDict()
        self.color_name_maps = OrderedDict()
        self.glyph = OrderedDict()
        self.ordinal_fields = []
        self.categorical_fields = []
        for f in self.config['summary_fields']:
            self.fields[f['name']] = None if f['field'] == 'None' else f['field']

            if 'cat_colors' in f.keys():
                self.colormaps[f['name']] = f['cat_colors']
                self.categorical_fields.append(f['field'])
                self.color_name_maps[f['name']] = f['cat_names']

            elif f['field'] != 'None':
                self.ordinal_fields.append(f['field'])

            if 'glyph' in f.keys():
                self.glyph[f['field']] = f['glyph']

        self.field = list(self.fields.values())[0]
        self.field_title = list(self.fields.keys())[0]

        self.colormap = None
        if self.colormaps:
            colormap = self.colormaps.get(self.field_title, None)
            if colormap:
                self.colormap = colormap
                self.colornames = self.color_name_maps[self.field_title]






    def load_datasets(self, outofcore):

        data_path = self.config['file']
        objpath = self.config.get('objpath', None)
        print('Loading Data from {} ! '.format(data_path))

        if not path.isabs(data_path):
            config_dir = path.split(self.config_path)[0]
            data_path = path.join(config_dir, data_path)

        if not path.exists(data_path):
            raise IOError('Unable to find input dataset: "{}"'.format(data_path))

        axes_fields = []
        for f in self.axes.values():
            axes_fields += [f['xaxis'], f['yaxis']]

        load_fields = [f for f in self.fields.values() if f is not None] + axes_fields

        if data_path.endswith(".csv"):
            self.df = pd.read_csv(data_path, usecols=load_fields)
            
            for f in self.categorical_fields:    # parse categorical fields
                self.df[f] = self.df[f].astype('category')
        elif data_path.endswith(".fits"):
            data_table = Table.read(data_path) 
            if ('LOGIMFWEIGHT' in data_table.keys()): data_table['LOGIMFWEIGHT'] = 10.**data_table['LOGIMFWEIGHT']
            data_table['g-r'] = data_table['UVIS_F606W'] - data_table['UVIS_F814W'] 
            data_table['UVIS_F814W'] *= -1. 
            data_table['UVIS_F606W'] *= -1. 
            self.df = data_table.to_pandas() 
            for f in self.categorical_fields:    # parse categorical fields
                self.df[f] = self.df[f].astype('category')
        else:
            raise IOError("Unknown data file type; only .csv currently supported")


    def prepare_dataframe(self): 
        print("inside prepare_dataframe") 
        print("Aperture inside prepare_dataframe: ", self.aperture, " meters") 
        print("Age      inside prepare_dataframe: ", self.age,      " Gyr   ") 
        
        


    @hold
    def create_aggregate(self, plot_width, plot_height, x_range, y_range, star_age, aperture, 
                         agg_field, x_field, y_field, agg_func, glyph):

        # this may not be the best place for it, but before we recreate the aggregation 
        # we need to edit the df according to the current slider settings, which are 
        # available here as "self.aperture", "self.age", etc. 
        self.prepare_dataframe() 

        canvas = ds.Canvas(plot_width=plot_width,plot_height=plot_height,
                           x_range=x_range,y_range=y_range)

        method = getattr(canvas, glyph)

        # handle categorical field
        if agg_field in self.categorical_fields:
            print("Categorical aggregate is about to do its thing with :", agg_field) 
            agg = method(self.df, x_field, y_field, ds.count_cat(agg_field))

        # handle ordinal field
        elif agg_field in self.ordinal_fields:
            func = self.aggregate_functions[agg_func]
            print("Ordinal aggregate is about to do its thing with :", agg_field) 
            agg = method(self.df[(self.df['LOGAGE'] == star_age) ], x_field, y_field, func(agg_field))
        else:
            print("Ordinal aggregate is about to do its thing with :", agg_field) 
            agg = method(self.df, x_field, y_field)

        return agg

    def render_image(self):

        if self.colormaps:
            colormap = self.colormaps.get(self.field_title, None)
            if colormap:
                self.colormap = colormap
                self.colornames = self.color_name_maps[self.field_title]

        pix = tf.shade(self.agg, cmap=self.color_ramp, color_key=self.colormap, how=self.transfer_function)

        if self.spread_size > 0:
            pix = tf.spread(pix, px=self.spread_size)

        return pix

class AppView(object):

    def __init__(self, app_model):
        self.model = app_model
        self.create_layout()

    def create_layout(self):
        # create figure
        self.x_range = Range1d(start=self.model.map_extent[0],
                               end=self.model.map_extent[2], bounds=None)
        self.y_range = Range1d(start=self.model.map_extent[3],
                               end=self.model.map_extent[1], bounds=None)
        self.fig = Figure(tools='wheel_zoom,pan,save,box_zoom', title='Color Magnitude Diagram',
                          x_range=self.x_range,
                          y_range=self.y_range,
                          lod_threshold=None,
                          plot_width=self.model.plot_width,
                          plot_height=self.model.plot_height,
                          background_fill_color='white')

        # Labeling will be used to deal with the fact that we cannot get the axes right 
        # this source can then be adjusted with sliders as necessary to reset axis. 
        label_source = ColumnDataSource(data={'x': [-5,-5,-5,-5,-5], 
                                        'y': [-10-0.2,-5-0.2,0-0.2,5-0.2,10-0.2], 'text':['10','5','0','-5','-10']}) 
        label1 = self.fig.text('x','y','text', source=label_source, text_font_size='8pt', text_color='deepskyblue') 

        # edit all the usual bokeh figure properties here 
        self.fig.xaxis.axis_label=self.model.xtitle 
        self.fig.yaxis.axis_label=self.model.ytitle 
        self.fig.yaxis.axis_label_text_font= 'PT Serif' 
        self.fig.yaxis.major_label_text_font = 'PT Serif' 
        self.fig.xaxis.axis_label_text_font= 'PT Serif' 
        self.fig.xaxis.major_label_text_font = 'PT Serif' 
        self.fig.min_border_top = 20
        self.fig.min_border_bottom = 10
        self.fig.min_border_left = 10
        self.fig.min_border_right = 10
        self.fig.axis.visible = False # use this to flip the axis labeling on and off 
        self.fig.xgrid.grid_line_color = '#aaaaaa' 
        self.fig.ygrid.grid_line_color = '#aaaaaa' 
        self.fig.ygrid.grid_line_alpha = 0.1  
        self.fig.xgrid.grid_line_alpha = 0.1  

        # add tiled basemap to class AppView 
        image_url    = 'http://server.arcgisonline.com/arcgis//rest/services/World_Imagery/MapServer/tile/{Z}/{Y}/{X}.png' 
        self.tile_source = WMTSTileSource(url=image_url) 
        self.tile_renderer = TileRenderer(tile_source=self.tile_source)
        self.tile_renderer.alpha = 0.02 
        self.fig.renderers.append(self.tile_renderer) # comment this out and it takes the ds points with it! WHY? 

        # add datashader layer - these are the aggregated data points to class AppView 
        self.image_source = ImageSource(url=self.model.service_url, extra_url_vars=self.model.shader_url_vars)
        self.image_renderer = DynamicImageRenderer(image_source=self.image_source)
        self.image_renderer.alpha = 1.00 
        self.fig.renderers.append(self.image_renderer)

        # add controls 
        controls = []            # empty list for astronomy controls 
        visual_controls = []     # empty list for visual controls 
        self.parameters = {}     # empty dict for astrophyscal pars 

        age_slider = Slider(title="Log Age [Gyr]", value=9.0, start=5.5, end=10.1, step=0.05)
        age_slider.on_change('value', self.on_age_change)
        controls.append(age_slider)
        self.parameters['age'] = age_slider.value 

        aperture_size_slider = Slider(title="Aperture [m]", value=10, start=2,end=20, step=1)
        aperture_size_slider.on_change('value', self.on_aperture_size_change)
        controls.append(aperture_size_slider)
        self.parameters['aperture'] = aperture_size_slider.value 

        exposure_time_slider = Slider(title="Exposure Time [hr]", value=0.1, start=1.0,end=10.0, step=0.1)
        exposure_time_slider.on_change('value', self.on_exposure_time_change)
        controls.append(exposure_time_slider)

        distance_slider = Slider(title="Distance [kpc]", value=100. , start=10.0,end=1000.0, step=100.)
        distance_slider.on_change('value', self.on_distance_change)
        controls.append(distance_slider)

        axes_select = Select(title='Variables', options=list(self.model.axes.keys()))
        axes_select.on_change('value', self.on_axes_change)
        controls.append(axes_select)

        self.field_select = Select(title='Field', options=list(self.model.fields.keys()))
        self.field_select.on_change('value', self.on_field_change)
        #controls.append(self.field_select) - chooses wich field to weight by in aggregation, temporarily omitted for devel 

        self.aggregate_select = Select(title='Aggregate', options=list(self.model.aggregate_functions.keys()))
        self.aggregate_select.on_change('value', self.on_aggregate_change)
        controls.append(self.aggregate_select)

        spread_size_slider = Slider(title="Spread Size (px)", value=1, start=0,end=5, step=1)
        spread_size_slider.on_change('value', self.on_spread_size_change)
        visual_controls.append(spread_size_slider)

        image_opacity_slider = Slider(title="Opacity", value=100, start=0,end=100, step=1)
        image_opacity_slider.on_change('value', self.on_image_opacity_slider_change)
        visual_controls.append(image_opacity_slider) 

        transfer_select = Select(title='Transfer Function', options=list(self.model.transfer_functions.keys()))
        transfer_select.on_change('value', self.on_transfer_function_change)
        visual_controls.append(transfer_select)

        color_ramp_select = Select(title='Colormap', name='Color Ramp', options=list(self.model.color_ramps.keys()))
        color_ramp_select.on_change('value', self.on_color_ramp_change)
        visual_controls.append(color_ramp_select)

        astro_tab = Panel(child=Column(children=controls), title='Stars') 
        visual_tab = Panel(child=Column(children=visual_controls), title='Visuals', width=450)

        self.controls = Tabs(tabs=[astro_tab, visual_tab], width=350)

        self.map_area = Column(width=900, height=600,children=[self.fig])
        self.layout = Row(width=1300, height=600,children=[self.controls, self.fig])
        self.model.fig = self.fig    # identify the fig defined here as the one that will be passed to AppView 

    def update_image(self):
        self.model.shader_url_vars['cachebust'] = str(uuid.uuid4())
        self.image_renderer.image_source = ImageSource(url=self.model.service_url, extra_url_vars=self.model.shader_url_vars)
        self.fig.xaxis.axis_label=self.model.active_axes['xtitle']  
        self.fig.yaxis.axis_label=self.model.active_axes['ytitle'] 

    def on_field_change(self, attr, old, new):
        self.model.field_title = new
        self.model.field = self.model.fields[new]

        self.update_image()

        if not self.model.field:
            self.aggregate_select.options = [("No Aggregates Available", "")]
        elif self.model.field in self.model.categorical_fields:
            self.aggregate_select.options = [("Categorical", "count_cat")]
        else:
            opts = [(k, k) for k in self.model.aggregate_functions.keys()]
            self.aggregate_select.options = opts

    def on_spread_size_change(self, attr, old, new):
        self.model.spread_size = int(new)
        self.update_image()

    def on_aperture_size_change(self, attr, old, new):
        self.model.aperture = int(new)
        self.update_image()

    def on_age_change(self, attr, old, new):
        self.model.age = new
        self.update_image()

    def on_exposure_time_change(self, attr, old, new):
        self.model.exposure_time = int(new)
        self.update_image()

    def on_distance_change(self, attr, old, new):
        self.model.distance = int(new)
        self.update_image()

    def on_axes_change(self, attr, old, new):
        print("self.model.axes ", self.model.axes) 
        self.model.active_axes = self.model.axes[new]
        self.update_image()

    def on_aggregate_change(self, attr, old, new):
        self.model.agg_function_name = new
        self.update_image()

    def on_transfer_function_change(self, attr, old, new):
        self.model.transfer_function = self.model.transfer_functions[new]
        self.update_image()

    def on_color_ramp_change(self, attr, old, new):
        self.model.color_ramp = self.model.color_ramps[new]
        self.update_image()

    def on_image_opacity_slider_change(self, attr, old, new):
        self.image_renderer.alpha = new / 100


if __name__ == '__main__':

    def add_roots(doc):
        model = AppState(False) # argument = "outofcore" = False by default 
        view = AppView(model)
        GetDataset.model = model  # GetDataset.model has type "AppState" 
        doc.add_root(view.layout) # view.layout has type "Row" 

    app = Application(FunctionHandler(add_roots))

    io_loop = IOLoop.current()

    server = Server({'/': app}, io_loop=io_loop, extra_patterns=[('/datashader', GetDataset)], port=5006)
    server.start()

    io_loop.add_callback(server.show, "/")
    io_loop.start()
