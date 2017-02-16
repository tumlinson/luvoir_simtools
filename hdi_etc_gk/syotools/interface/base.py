#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 19 12:43:00 2016

@author: gkanarek, tumlinson
"""

import yaml

#Bokeh imports
from bokeh.client import push_session
from bokeh.embed import autoload_server, components,  file_html
from bokeh.io import curdoc, output_file
from bokeh.layouts import column, gridplot, row, widgetbox
from bokeh.models.callbacks import CustomJS
from bokeh.models.glyphs import Segment, Text
from bokeh.models.layouts import HBox, VBoxForm
from bokeh.models.markers import Circle, Square
from bokeh.models.ranges import Range1d
from bokeh.models.sources import ColumnDataSource
from bokeh.models.tools import BoxSelectTool, HoverTool
from bokeh.models.widgets.groups import RadioButtonGroup
from bokeh.models.widgets.inputs import Slider, TextInput
from bokeh.models.widgets.markups import Div, Paragraph
from bokeh.models.widgets.panels import Panel, Tabs
from bokeh.plotting import figure, show
from bokeh.resources import CDN
from bokeh.themes import Theme



class SYOTool(object):
    """
    This is a framework for quickly generating Bokeh tools for Science Yield
    Optimization. Much of the Bokeh machinery will be kept under the hood in
    this class. To create a new tool, simply subclass SYOTool, set some
    parameters, connect with some astronomical models, and output embeddable 
    HTML.
    
    One major update is to use .yaml files as a templating method (a la the
    kv language in Kivy) to allow for quick and easy human-readable Bokeh
    interface construction.
    """
    
    template = ""
    
    def load_string(self, template_string):
        pass
    
    def load_file(self, template_file):
        pass


    