
from bokeh.models import Range1d, ColumnDataSource
import numpy as np 

def set_bullseye_plot_options(plot):

    plot.x_range=Range1d(-50,50,bounds=(-50,50))
    plot.y_range=Range1d(-50,50,bounds=(-50,50))
    plot.background_fill_color = "#1D1B4D"
    plot.background_fill_color = "black"
    plot.background_fill_alpha = 1.0
    plot.yaxis.axis_label = 'Expected Number of Detected Planets'
    plot.xaxis.axis_label = ' '
    plot.xaxis.axis_line_width = 0
    plot.yaxis.axis_line_width = 0
    plot.xaxis.axis_line_color = '#1D1B4D'
    plot.yaxis.axis_line_color = '#1D1B4D'
    plot.border_fill_color = "#1D1B4D"
    plot.min_border_left = 10
    plot.min_border_right = 10

    plot.text(0.95*0.707*np.array([10., 20., 30., 40.]), 0.707*np.array([10., 20., 30., 40.]), \
         text=['10 pc', '20 pc', '30 pc', '40 pc'], text_color="white", text_font_style='bold', text_font_size='12pt', text_alpha=0.8)
    plot.text([48.5], [47], ['Chance Of Detecting a'], text_color="#BAD8FF", text_align="right")
    plot.text([48.5], [44.5], ['Habitable Planet Candidate'], text_color="#BAD8FF", text_align="right")
    plot.text([48.5], [42.0], ['if Present'], text_color="#BAD8FF", text_align="right")
    plot.text([48.5], [42.0], ['___________'], text_color="#BAD8FF", text_align="right")
    plot.text(np.array([48.5]), np.array([39.5]), ["80-100%"], text_color='#F59A0A', text_alpha=0.6+0.2, text_align="right")
    plot.text(np.array([48.5]), np.array([39.5-1*2.4]), ["50-80%"], text_color='#F59A0A', text_alpha=0.3+0.2, text_align="right")
    plot.text(np.array([48.5]), np.array([39.5-2*2.4]), ["20-50%"], text_color='#F59A0A', text_alpha=0.1+0.2, text_align="right")
    plot.text(np.array([48.5]), np.array([39.5-3*2.4]), ["Not Observed"], text_color='#1D1B4D', text_align="right")
    plot.text([-49], [46], ['Habitable Candidate Detections'], text_font_size='16pt', text_color='#66A0FE')
    plot.text([-49], [43], ['Random Realization for One Year Survey'], text_font_size='16pt', text_color='#66A0FE')
    plot.circle([0], [0], radius=0.1, fill_alpha=1.0, line_color='white', fill_color='white')
    plot.circle([0], [0], radius=0.5, fill_alpha=0.0, line_color='white')
    
def set_hist_plot_options(plot):
    plot.title.text_font_size = '14pt'
    plot.title.text_color='white'
    plot.background_fill_color = "#1D1B4D"
    plot.background_fill_alpha = 1.0
    plot.yaxis.axis_label = 'Number of Detected Planets'
    plot.xaxis.axis_label = ' '
    plot.xaxis.axis_line_width = 2
    plot.yaxis.axis_line_width = 2
    plot.xaxis.axis_line_color = '#1D1B4D'
    plot.yaxis.axis_line_color = '#1D1B4D'
    plot.border_fill_color = "#1D1B4D"
    plot.min_border_left = 0
    plot.min_border_bottom = 20
    plot.image_url(url=["http://www.jt-astro.science/planet_background_v1.png"], x=[-0.05], y=[300], w=[5.0], h=[300])
    plot.text([0.45], [265], ['Rocky'], text_align='center', text_font_size='11pt', text_color='black')
    plot.text([1.45], [280], ['Super-Earths'], text_align='center', text_font_size='11pt', text_color='black')
    plot.text([2.45], [265], ['Sub-Neptunes'], text_align='center', text_font_size='11pt', text_color='black')
    plot.text([3.45], [280], ['Neptunes'], text_align='center', text_font_size='11pt', text_color='black')
    plot.text([4.45], [265], ['Jupiters'], text_align='center', text_font_size='11pt', text_color='black')
    plot.title.align='center'


