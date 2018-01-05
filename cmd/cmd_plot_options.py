
from bokeh.models import Range1d, ColumnDataSource

def set_plot_options(plot):
    plot.background_fill_alpha = 1.0
    plot.yaxis.axis_label = 'F814W' 
    plot.xaxis.axis_label = 'F606W - F814W' 
    plot.xaxis.axis_line_width = 0
    plot.x_range=Range1d(-2,4.0,bounds=(-2,4.0)) # width = 4 units 
    plot.y_range=Range1d(-14,7,bounds=(-14,7)) # height = 20 units 
    plot.yaxis.axis_line_width = 0 
    plot.xaxis.axis_line_color = 'white' 
    plot.yaxis.axis_line_color = 'white' 
    plot.min_border_left = 0
    plot.min_border_right = 10
    plot.outline_line_color = 'white' 


    plot.axis.visible = False # use this to flip the axis labeling on and off 

    y_label_source = ColumnDataSource(data={'x': [-1.3,-1.3,-1.3,-1.3,-1.3],
                                        'y': [-10-0.4,-5-0.4,0-0.4,5-0.4,10-0.4], 'text':['10','5','0','-5','-10']})
    x_label_source = ColumnDataSource(data={'x': [-1.0,0.0,1.0,2.0, 3.0],
                                        'y': [-13.5-0.2,-13.5-0.2,-13.5-0.2,-13.5-0.2,-13.5-0.2], 'text':['-1','0','1','2','3']})
    plot.text('x','y','text', source=x_label_source, text_align='center', text_font_size='15pt', text_color='black')
    plot.text('x','y','text', source=y_label_source, text_font_size='15pt', text_color='black', text_align='right')

    plot.quad(top=[0], bottom=[-13.0], left=[4.0], right=[4.4], fill_alpha=1, fill_color='white', line_width=1, line_color='orange') 
    plot.quad(top=[7], bottom=[-13.0], left=[-1.2], right=[4.0], fill_alpha=0, line_width=1, line_color='black') 

