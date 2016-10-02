
''' A dead simple ETC for HDST 
'''
import numpy as np
from bokeh.io import output_file, gridplot 

from bokeh.plotting import Figure
from bokeh.resources import CDN
from bokeh.embed import components, autoload_server 
from bokeh.models import ColumnDataSource, HBox, VBoxForm, HoverTool, Paragraph, Range1d 
from bokeh.layouts import column, row, WidgetBox 
from bokeh.models.widgets import Slider
from bokeh.io import hplot, vplot, curdoc
from bokeh.embed import file_html


def compute_snr(aperture, exposure_in_hours, ab_magnitudes):
    # this will be a plain python function that will produce the SNR numbers

    diff_limit = 1.22*(500.*0.000000001)*206264.8062/aperture
    print 'diff_limit', diff_limit

    pixel_size = np.array([0.016, 0.016, 0.016, 0.016, 0.016, 0.016, 0.016, 0.04, 0.04, 0.04])

    source_magnitudes = np.array([1., 1., 1., 1., 1., 1., 1.]) * ab_magnitudes
    central_wavelength = np.array([155., 228., 360., 440., 550., 640., 790., 1260., 1600., 2220.])
    ab_zeropoint = np.array([35548., 24166., 15305., 12523., 10018., 8609., 6975., 4373., 3444., 2482.])
    total_qe = np.array([0.1, 0.1, 0.15, 0.45, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6])
    aperture_correction = np.array([1., 1., 1., 1., 1., 1., 1., 1., 1., 1.])
    bandpass_r = np.array([5., 5., 5., 5., 5., 5., 5., 5., 5., 5.])
    derived_bandpass = central_wavelength / bandpass_r
    # two efficiency factors omitted

    detector_read_noise = np.array([3., 3., 3., 3., 3., 3., 3., 4., 4., 4.])
    dark_current = np.array([0.0005, 0.0005, 0.001, 0.001, 0.001, 0.001, 0.001, 0.002, 0.002, 0.002])
    sky_brightness = np.array([23.807, 25.517, 22.627, 22.307, 21.917, 22.257, 21.757, 21.567, 22.417, 22.537])
    fwhm_psf = 1.22 * central_wavelength * 0.000000001 * 206264.8062 / aperture
    fwhm_psf[fwhm_psf < diff_limit] = fwhm_psf[fwhm_psf < diff_limit] * 0.0 + diff_limit

    sn_box = np.round(3. * fwhm_psf / pixel_size)

    number_of_exposures = np.array([3., 3., 3., 3., 3., 3., 3., 3., 3., 3.])

    desired_exposure_time = np.array([1., 1., 1., 1., 1., 1., 1., 1., 1., 1.]) * exposure_in_hours * 3600.

    time_per_exposure = desired_exposure_time / number_of_exposures

    signal_counts = total_qe * desired_exposure_time * ab_zeropoint * aperture_correction * 0.7854 * \
        (aperture * 100.0)**2 * derived_bandpass * 10.**(-0.4*ab_magnitudes)

    shot_noise_in_signal = signal_counts ** 0.5

    sky_counts = total_qe * desired_exposure_time * ab_zeropoint * 0.7854 * (aperture * 100.0)**2 * \
        derived_bandpass * 10.**(-0.4*sky_brightness) * (pixel_size * sn_box)**2

    shot_noise_in_sky = sky_counts ** 0.5

    read_noise = detector_read_noise * sn_box * number_of_exposures**0.5

    dark_noise = sn_box * (dark_current * desired_exposure_time)**0.5

    snr = signal_counts / (signal_counts + sky_counts + read_noise**2 + dark_noise**2)**0.5


    print
    print
    print
    print 'source_mag', source_magnitudes
    print 'central wave', central_wavelength
    print 'ab zeropoints', ab_zeropoint
    print 'total_qe', total_qe
    print 'ap corr', aperture_correction
    print 'bandpass R', bandpass_r
    print 'derived_bandpass', derived_bandpass
    print 'read_noise', detector_read_noise
    print 'dark rate', dark_current
    print 'sky_brightness', sky_brightness
    print 'fwhm_psf', fwhm_psf
    print 'sn_box', sn_box
    print 'number_of_exposures', number_of_exposures
    print 'detector_read_noise', detector_read_noise
    print 'time_per_exp', time_per_exposure
    print 'signal_counts', signal_counts
    print 'shot_noise_in_signal', shot_noise_in_signal
    print 'sky_counts', sky_counts
    print 'shot_noise_in_sky', shot_noise_in_sky
    print 'read noise', read_noise
    print 'dark noise', dark_noise
    print 'SNR', snr, np.max(snr)
    print
    print
    print

    return snr

# create a new plot
x = list(range(11))
y0 = x
y1 = [10 - i for i in x]
y2 = [abs(i - 5) for i in x]
counts_plot = Figure(plot_width=400, plot_height=400, title=None)
counts_plot.background_fill_color = "beige"
counts_plot.background_fill_alpha = 0.5
counts_plot.circle(x, y0, size=10, color="navy", alpha=0.5)


# Set up data
# crude numbers taken from Postman's excel spreadsheet 
wave = np.array([155., 228., 360., 440., 550., 640., 790., 1260., 1600., 2220.]) 
snr = compute_snr(12., 1., 32.)
source = ColumnDataSource(data=dict(x=wave[2:-3], y=snr[2:-3], desc=['U','B','V','R','I']))
source2 = ColumnDataSource(data=dict(x=[155., 228.], y=snr[0:2], desc=['FUV', 'NUV']))
source3 = ColumnDataSource(data=dict(x=[1260., 1600., 2220.], y=snr[-3:], desc=['J', 'H', 'K']))

hover = HoverTool(point_policy="snap_to_data", 
        tooltips="""
        <div>
            <div>
                <span style="font-size: 17px; font-weight: bold; color: #696">@desc band</span>
            </div>
            <div>
                <span style="font-size: 15px; font-weight: bold; color: #696">S/N = </span>
                <span style="font-size: 15px; font-weight: bold; color: #696;">@y</span>
            </div>
        </div>
        """
    )

# Set up plot
snr_plot = Figure(plot_height=400, plot_width=800, title="LUVOIR Photometric ETC",
              tools="crosshair,pan,reset,resize,save,box_zoom,wheel_zoom",
              x_range=[120, 2300], y_range=[0, 40], toolbar_location='right')
snr_plot.x_range = Range1d(120, 2300, bounds=(120, 2300)) 
snr_plot.add_tools(hover)
snr_plot.background_fill_color = "beige"
snr_plot.background_fill_alpha = 0.5
snr_plot.yaxis.axis_label = 'SNR'
snr_plot.xaxis.axis_label = 'Wavelength (nm)'
snr_plot.text(5500, 20, text=['V'], text_align='center', text_color='red')

snr_plot.line('x', 'y', source=source, line_width=3, line_alpha=1.0) 
snr_plot.circle('x', 'y', source=source, fill_color='white', line_color='blue', size=10)
    
snr_plot.line('x', 'y', source=source2, line_width=3, line_color='orange', line_alpha=1.0)
snr_plot.circle('x', 'y', source=source2, fill_color='white', line_color='orange', size=8) 
    
snr_plot.line('x', 'y', source=source3, line_width=3, line_color='red', line_alpha=1.0)
snr_plot.circle('x', 'y', source=source3, fill_color='white', line_color='red', size=8) 

# Set up widgets
aperture= Slider(title="Aperture (meters)", value=12., start=2., end=20.0, step=1.0)
exptime = Slider(title="Exptime (hours)", value=1., start=0., end=10.0, step=0.1)
magnitude = Slider(title="Magnitude (AB)", value=32.0, start=10.0, end=35.)

def update_data(attrname, old, new):

    # Get the current slider values
    a = aperture.value 
    m = magnitude.value
    e = exptime.value

    wave = np.array([155., 228., 360., 440., 550., 640., 790., 1260., 1600., 2220.]) 
    snr = compute_snr(a, e, m) 
    source.data = dict(x=wave[2:-3], y=snr[2:-3], size=np.array([0.01,0.02,0.03,0.04,0.05]) * a,  desc=['U','B','V','R','I']) 
    source2.data = dict(x=[155., 228.], y=snr[0:2], desc=['FUV','NUV']) 
    source3.data = dict(x=[1260., 1600., 2220.], y=snr[-3:], desc=['J','H','K']) 

# iterate on changes to parameters 
for w in [aperture, exptime, magnitude]: 
    w.on_change('value', update_data)

# Set up layouts and add to document
#inputs = VBoxForm(children=[aperture, exptime, magnitude]) 
inputs = WidgetBox(children=[aperture, exptime, magnitude]) 
curdoc().add_root(row(children=[inputs, snr_plot])) 

script = autoload_server(model=None, app_path="/simple_etc", url="pancho.local:5006")
print(script)
