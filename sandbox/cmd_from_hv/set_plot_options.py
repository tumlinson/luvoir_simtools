
from bokeh.models import Range1d

def set_plot_options(plot):
    plot.background_fill_alpha = 1.0
    plot.yaxis.axis_label = 'F814W' 
    plot.xaxis.axis_label = 'g-r' 
    plot.xaxis.axis_line_width = 0
    plot.x_range=Range1d(-1,3,bounds=(-1,3)) # width = 4 units 
    plot.y_range=Range1d(-13,7,bounds=(-13,7)) # height = 20 units 
    plot.yaxis.axis_line_width = 0 
    plot.xaxis.axis_line_color = 'black' 
    plot.yaxis.axis_line_color = 'black' 
    plot.min_border_left = 10
    plot.min_border_right = 10

