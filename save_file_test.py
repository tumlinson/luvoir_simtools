import numpy as np
from astropy.io import fits, ascii 
from astropy.table import Table, Column

import os 

from bokeh.io import output_file, show
from bokeh.layouts import widgetbox, Column
from bokeh.plotting import figure, gridplot, output_file, show
from bokeh.models import ColumnDataSource, HBox, VBoxForm, HoverTool, Paragraph, Range1d
from bokeh.io import hplot, vplot, curdoc
from bokeh.models import HoverTool
from bokeh.models.widgets import Slider, Div, TextInput, RadioButtonGroup

text_input = TextInput(value="filename", title="File Rootname:", width=100)
p = Div(text="""Your file is <a href='http://www.stsci.edu'>here</a>.""", width=300, height=100)
format_button_group = RadioButtonGroup(labels=["csv", "fits"])

a = np.array([1, 4], dtype=np.int32)
b = [2.0, 5.0]
c = ['x'*100, 'y'*100]
t = Table([a, b, c], names=('a', 'b', 'c'))

def change_filename(attrname, old, new): 
   format_button_group.active = None 


def i_clicked_a_button(new): 
   filename=text_input.value + {0:'.csv', 1:'.fits'}[format_button_group.active]
   print "Your format is   ", format_button_group.active, {0:'csv', 1:'fits'}[format_button_group.active] 
   print "Your filename is: ", filename 
   fileformat={0:'csv', 1:'fits'}[format_button_group.active]
   t['c'] = [filename,filename] 
   p.text = """Your file is <a href='http://www.stsci.edu/~tumlinso/"""+filename+""".gz'>"""+filename+""".gz</a>. """

   if (format_button_group.active == 1): t.write(filename, overwrite=True) 
   if (format_button_group.active == 0): ascii.write(t, filename)

   os.system('gzip -f ' +filename) 
   os.system('cp -rp '+filename+'.gz /grp/webpages/tumlinso/')
   print    """Your file is <a href='http://www.stsci.edu/~tumlinso/"""+filename+""".gz'>"""+filename+""".gz</a>. """


for w in [text_input]: 
    w.on_change('value', change_filename)
format_button_group.on_click(i_clicked_a_button)

v = Column(children=[text_input, format_button_group, p])

curdoc().add_root(v)


